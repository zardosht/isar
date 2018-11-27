import logging
import time

from PyQt5 import QtWidgets, uic, QtCore
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QListWidget, QPushButton, QWidget, QLabel, QDialog

from isar.camera.camera import CameraService
from isar.scene import model
from isar.services import servicemanager
from isar.services.servicemanager import ServiceNames

logger = logging.getLogger("isar.scene")


class SceneDefinitionWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setup_ui()

        self._camera_service: CameraService = None
        self.setup_camera_service()

        self._timer = None
        self.setup_timer()

        # self.setAttribute(QtCore.Qt.WA_QuitOnClose, True)
        self.setup_models()

    def setup_ui(self):
        uic.loadUi("isar/ui/scene_definition.ui", self)
        self.new_scene_btn.clicked.connect(self.aaa)

    def aaa(self):
        self.scenes_view.model().change_scene_name("aa" + str(time.time()))

    def setup_camera_service(self):
        self._camera_service = servicemanager.get_service(ServiceNames.CAMERA1)
        self._camera_service.start_capture()

    def setup_timer(self):
        self._timer = QTimer()
        self._timer.timeout.connect(self.update_camera_view)
        self._timer.start(5)

    def setup_models(self):
        scenes_model = model.create_dummy_scenes_model()
        self.scenes_view.setModel(scenes_model)

    def update_camera_view(self):
        camera_frame = self._camera_service.get_frame()
        img = camera_frame.image
        qfromat = QImage.Format_Indexed8

        if len(img.shape) == 3: # sahpe[0] = rows, [1] = cols, [2] = channels
            if img.shape[2] == 4:
                qfromat = QImage.Format_RGBA8888
            else:
                qfromat = QImage.Format_RGB888

        out_image = QImage(img, img.shape[1], img.shape[0], img.strides[0], qfromat)
        out_image = out_image.rgbSwapped()
        self.camera_view.setPixmap(QPixmap.fromImage(out_image))
        self.camera_view.setScaledContents(True)

    def closeEvent(self, QCloseEvent):
        self._timer.stop()
        self._camera_service.stop_capture()



# OpenCV Python GUI Development Tutorial 10: Display WebCam Video Feed on QLabel
#
# https://www.youtube.com/watch?v=MUpC6z32bCA
#
'''
* Import


'''

