import os

import numpy as np

from qtpy import QtWidgets, QtGui
from qtpy.QtCore import Qt

from glue.external.echo.qt import autoconnect_callbacks_to_qt
from glue.utils.qt import load_ui, fix_tab_widget_fontsize


class ScatterLayerStyleEditor(QtWidgets.QWidget):

    def __init__(self, layer, parent=None):

        super(ScatterLayerStyleEditor, self).__init__(parent=parent)

        self.ui = load_ui('layer_style_editor.ui', self,
                          directory=os.path.dirname(__file__))

        connect_kwargs = {'alpha': dict(value_range=(0, 1)),
                          'size_scaling': dict(value_range=(0.1, 10), log=True),
                          'vector_scaling': dict(value_range=(0.1, 10), log=True)}
        autoconnect_callbacks_to_qt(layer.state, self.ui, connect_kwargs)

        fix_tab_widget_fontsize(self.ui.tab_widget)

        self.layer_state = layer.state

        self.layer_state.add_callback('markers_visible', self._update_markers_visible)
        self.layer_state.add_callback('line_visible', self._update_line_visible)
        self.layer_state.add_callback('xerr_visible', self._update_xerr_visible)
        self.layer_state.add_callback('yerr_visible', self._update_yerr_visible)
        self.layer_state.add_callback('vector_visible', self._update_vectors_visible)

        self.layer_state.add_callback('cmap_mode', self._update_cmap_mode)
        self.layer_state.add_callback('size_mode', self._update_size_mode)
        self.layer_state.add_callback('vector_mode', self._update_vector_mode)

        self.layer_state.add_callback('layer', self._update_warnings)

        self._update_markers_visible()
        self._update_line_visible()
        self._update_xerr_visible()
        self._update_yerr_visible()
        self._update_vectors_visible()

        self._update_size_mode()
        self._update_vector_mode()
        self._update_cmap_mode()

        self._update_warnings()

    def _update_warnings(self):

        if self.layer_state.layer is None:
            n_points = 0
        else:
            n_points = np.product(self.layer_state.layer.shape)

        warning = " (may be slow given data size)"

        for combo, threshold in [(self.ui.combosel_size_mode, 10000),
                                 (self.ui.combosel_cmap_mode, 50000)]:

            if n_points > threshold:
                for item in range(combo.count()):
                    text = combo.itemText(item)
                    if text != 'Fixed':
                        combo.setItemText(item, text + warning)
                        combo.setItemData(item, QtGui.QBrush(Qt.red), Qt.TextColorRole)
            else:
                for item in range(combo.count()):
                    text = combo.itemText(item)
                    if text != 'Fixed':
                        if warning in text:
                            combo.setItemText(item, text.replace(warning, ''))
                            combo.setItemData(item, QtGui.QBrush(), Qt.TextColorRole)

        if n_points > 10000:
            self.ui.label_warning_errorbar.show()
        else:
            self.ui.label_warning_errorbar.hide()

        if n_points > 10000:
            self.ui.label_warning_vector.show()
        else:
            self.ui.label_warning_vector.hide()

    def _update_size_mode(self, size_mode=None):

        if self.layer_state.size_mode == 'Fixed':
            self.ui.label_size_attribute.hide()
            self.ui.combosel_size_att.hide()
            self.ui.label_size_limits.hide()
            self.ui.valuetext_size_vmin.hide()
            self.ui.valuetext_size_vmax.hide()
            self.ui.button_flip_size.hide()
            self.ui.value_size.show()
        else:
            self.ui.label_size_attribute.show()
            self.ui.combosel_size_att.show()
            self.ui.label_size_limits.show()
            self.ui.valuetext_size_vmin.show()
            self.ui.valuetext_size_vmax.show()
            self.ui.button_flip_size.show()
            self.ui.value_size.hide()

    def _update_markers_visible(self, *args):
        self.ui.combosel_size_mode.setEnabled(self.layer_state.markers_visible)
        self.ui.value_size.setEnabled(self.layer_state.markers_visible)
        self.ui.combosel_size_att.setEnabled(self.layer_state.markers_visible)
        self.ui.valuetext_size_vmin.setEnabled(self.layer_state.markers_visible)
        self.ui.valuetext_size_vmax.setEnabled(self.layer_state.markers_visible)
        self.ui.button_flip_size.setEnabled(self.layer_state.markers_visible)
        self.ui.value_size_scaling.setEnabled(self.layer_state.markers_visible)

    def _update_line_visible(self, *args):
        self.ui.value_linewidth.setEnabled(self.layer_state.line_visible)
        self.ui.combosel_linestyle.setEnabled(self.layer_state.line_visible)

    def _update_xerr_visible(self, *args):
        self.ui.combosel_xerr_att.setEnabled(self.layer_state.xerr_visible)

    def _update_yerr_visible(self, *args):
        self.ui.combosel_yerr_att.setEnabled(self.layer_state.yerr_visible)

    def _update_vectors_visible(self, *args):
        self.ui.combosel_vector_mode.setEnabled(self.layer_state.vector_visible)
        self.ui.combosel_vx_att.setEnabled(self.layer_state.vector_visible)
        self.ui.combosel_vy_att.setEnabled(self.layer_state.vector_visible)
        self.ui.value_vector_scaling.setEnabled(self.layer_state.vector_visible)
        self.ui.combosel_vector_origin.setEnabled(self.layer_state.vector_visible)
        self.ui.bool_vector_arrowhead.setEnabled(self.layer_state.vector_visible)

    def _update_vector_mode(self, vector_mode=None):
        if self.layer_state.vector_mode == 'Cartesian':
            self.ui.label_vector_x.setText('vx')
            self.ui.label_vector_y.setText('vy')
        elif self.layer_state.vector_mode == 'Polar':
            self.ui.label_vector_x.setText('angle (deg)')
            self.ui.label_vector_y.setText('length')

    def _update_cmap_mode(self, cmap_mode=None):

        if self.layer_state.cmap_mode == 'Fixed':
            self.ui.label_cmap_attribute.hide()
            self.ui.combosel_cmap_att.hide()
            self.ui.label_cmap_limits.hide()
            self.ui.valuetext_cmap_vmin.hide()
            self.ui.valuetext_cmap_vmax.hide()
            self.ui.button_flip_cmap.hide()
            self.ui.combodata_cmap.hide()
            self.ui.label_colormap.hide()
            self.ui.color_color.show()
        else:
            self.ui.label_cmap_attribute.show()
            self.ui.combosel_cmap_att.show()
            self.ui.label_cmap_limits.show()
            self.ui.valuetext_cmap_vmin.show()
            self.ui.valuetext_cmap_vmax.show()
            self.ui.button_flip_cmap.show()
            self.ui.combodata_cmap.show()
            self.ui.label_colormap.show()
            self.ui.color_color.hide()