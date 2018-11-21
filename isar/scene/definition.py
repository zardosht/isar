import logging
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QListWidget, QPushButton, QWidget, QLabel

logger = logging.getLogger("isar.StartMenuWindow")


class SceneDefinitionWindow(QWidget):
    def __init__(self):
        super().__init__()
        # self.init_ui2()
        # self.init_ui()
        self.init_ui3()

    def init_ui3(self):
        uic.loadUi("ui/scene_definition.ui", self)

    def init_ui2(self):
        okButton = QPushButton("OK")
        cancelButton = QPushButton("Cancel")

        hbox = QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(okButton)
        hbox.addWidget(cancelButton)

        vbox = QVBoxLayout()
        vbox.addStretch(1)
        vbox.addLayout(hbox)

        self.setLayout(vbox)

        self.setGeometry(300, 300, 300, 150)
        self.setWindowTitle('Buttons')

    def init_ui(self):
        main_hlayout = QHBoxLayout()
        main_hlayout.addStretch(1)
        # main_hlayout.setContentsMargins(0, 0, 0, 0)

        # ====== Scene List =========
        scenes_layout = QVBoxLayout()
        scenes_layout.addStretch(1)
        # scenes_layout.setContentsMargins(0, 0, 0, 0)

        scences = QListWidget()
        scences.addItem("Scene 1")
        scences.addItem("Scene 2")
        scenes_layout.addWidget(scences)

        add_scene_btn = QPushButton()
        add_scene_btn.setText("Add")
        scenes_layout.addWidget(add_scene_btn)

        remove_scene_btn = QPushButton()
        remove_scene_btn.setText("Remove")
        scenes_layout.addWidget(remove_scene_btn)

        main_hlayout.addLayout(scenes_layout)

        # ====== Camera Widget and Pallet =========
        vlayout1 = QVBoxLayout()
        vlayout1.addStretch(1)

        camera_widget = CameraWidget()
        vlayout1.addWidget(camera_widget)

        pallet = QHBoxLayout()
        pallet.addStretch(1)

        label = QLabel()
        label.setText("Annotations")
        pallet.addWidget(label)

        text_btn = QPushButton()
        text_btn.setText("Text")
        pallet.addWidget(text_btn)

        arrow_btn = QPushButton()
        arrow_btn.setText("Arrow")
        pallet.addWidget(arrow_btn)

        vlayout1.addLayout(pallet)
        main_hlayout.addLayout(vlayout1)

        # ====== Objects =========
        objects_layout = QVBoxLayout()
        objects_layout.addStretch(1)

        objects = QListWidget()
        objects.addItem("Pincers")
        objects.addItem("Linemans Pliers")
        objects_layout.addWidget(objects)

        main_hlayout.addLayout(objects_layout)

        # ====== Properties =========
        properties = PropertiesWidget()
        main_hlayout.addWidget(properties)

        self.setLayout(main_hlayout)


class CameraWidget(QWidget):
    def __init__(self):
        super().__init__()


class PropertiesWidget(QWidget):
    def __init__(self):
        super().__init__()