from __future__ import absolute_import, division, print_function

from qtpy import QtCore, QtWidgets
from qtpy.QtCore import Qt
from glue.core.callback_property import add_callback
from glue.utils import nonpartial
from glue.viewers.common.qt.mode import CheckableMode, NonCheckableMode



class BasicToolbar(QtWidgets.QToolBar):

    mode_activated = QtCore.Signal()
    mode_deactivated = QtCore.Signal()

    def __init__(self, parent):
        """
        Create a new toolbar object
        """

        super(BasicToolbar, self).__init__(parent=parent)

        self.buttons = {}
        self.setIconSize(QtCore.QSize(25, 25))
        self.layout().setSpacing(1)
        self.setFocusPolicy(Qt.StrongFocus)
        self._mode = None

    @property
    def mode(self):
        return self._mode

    @mode.setter
    def mode(self, new_mode):

        old_mode = self._mode

        # If the mode is as before, we don't need to do anything
        if old_mode is new_mode:
            return

        # Otheriwse, if the mode changes, then we need to disable the previous
        # mode...
        if old_mode is not None:
            self.deactivate_mode(old_mode)
            if isinstance(old_mode, CheckableMode):
                button = self.buttons[old_mode.mode_id]
                if button.isChecked():
                    button.blockSignals(True)
                    button.setChecked(False)
                    button.blockSignals(False)

        # ... and enable the new one
        if new_mode is not None:
            self.activate_mode(new_mode)
            if isinstance(new_mode, CheckableMode):
                button = self.buttons[new_mode.mode_id]
                if button.isChecked():
                    button.blockSignals(True)
                    button.setChecked(True)
                    button.blockSignals(False)

        if isinstance(new_mode, CheckableMode):
            self._mode = new_mode
            self.mode_activated.emit()
        else:
            self._mode = None
            self.mode_deactivated.emit()

    def enable_mode(self, mode):
        pass

    def disable_mode(self, mode):
        pass

    def add_mode(self, mode):

        parent = QtWidgets.QToolBar.parent(self)

        action = QtWidgets.QAction(mode.icon, mode.action_text, parent)

        def toggle(checked):
            if checked:
                self.mode = mode
            else:
                self.mode = None

        def trigger(checked):
            self.mode = mode

        parent.addAction(action)

        if isinstance(mode, CheckableMode):
            action.toggled.connect(toggle)
        else:
            action.triggered.connect(trigger)

        if mode.shortcut is not None:
            action.setShortcut(mode.shortcut)
            action.setShortcutContext(Qt.WidgetShortcut)

        action.setToolTip(mode.tool_tip)
        action.setCheckable(isinstance(mode, CheckableMode))
        self.buttons[mode.mode_id] = action

        menu_actions = mode.menu_actions()
        if len(menu_actions) > 0:
            menu = QtWidgets.QMenu(self)
            for ma in mode.menu_actions():
                ma.setParent(self)
                menu.addAction(ma)
            action.setMenu(menu)
            menu.triggered.connect(nonpartial(toggle))

        self.addAction(action)

        return action
