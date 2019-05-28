import logging

from PyQt5 import uic
from PyQt5.QtWidgets import QDialog


logger = logging.getLogger("isar.scene.physicalobjecttool")


class EventsActionsRulesDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        uic.loadUi("isar/ui/events_actions_rules_dialog.ui", self)




