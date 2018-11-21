import logging
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QListWidget, QPushButton, QWidget, QLabel

logger = logging.getLogger("isar.StartMenuWindow")


class SceneDefinitionWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        uic.loadUi("ui/scene_definition.ui", self)




