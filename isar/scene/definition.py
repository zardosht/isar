import logging
from PyQt5 import QtWidgets, uic, QtCore
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QListWidget, QPushButton, QWidget, QLabel, QDialog

from isar.camera.camera import CameraService
from isar.services import servicemanager

logger = logging.getLogger("isar.scene")


class SceneDefinitionWindow(QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi("ui/scene_definition.ui", self)

        # self.setAttribute(QtCore.Qt.WA_QuitOnClose, True)

        self.camera_service: CameraService = servicemanager.services[CameraService.service_name]
        self.camera_service.start_capture()

        self._timer = QTimer()
        self._timer.timeout.connect(self.update_camera_view)
        self._timer.start(5)

    def update_camera_view(self):
        camera_frame = self.camera_service.get_frame()
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
        self.camera_service.stop_capture()



# OpenCV Python GUI Development Tutorial 10: Display WebCam Video Feed on QLabel
#
# https://www.youtube.com/watch?v=MUpC6z32bCA
#
'''
* Import


'''

