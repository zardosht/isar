import logging
import multiprocessing
import threading
import time

import cv2
import numpy as np
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QPixmap

from isar import services
from isar.scene import util
from isar.scene.scenemodel import ScenesModel
from isar.scene.util import Frame
from isar.services import servicemanager
from isar.services.service import Service


logger = logging.getLogger("isar.projection.projector")


def init_projector(screen_id):
    global projector
    projector = QtWidgets.QApplication.desktop().screenGeometry(screen_id)


def is_ready():
    if not projector:
        init_projector()
    return projector is not None and projector.width() != 0


def get_projector_geometry():
    if projector is not None:
       return projector.left(), projector.top(), projector.width(), projector.height()
    else:
        raise RuntimeError("Projector is not ready!")


class ProjectorView(QtWidgets.QLabel):
    def __init__(self, top, left, scene_size):
        super().__init__()

        self.scene_size = scene_size
        self.scene_image = None
        self.calibration_matrix = np.identity(3, dtype=np.float64)

    # def paintEvent(self, event):
    #     qpainter = QtGui.QPainter()
    #     qpainter.begin(self)
    #     if self.image:
    #         qpainter.drawImage(QtCore.QPoint(0, 0), self.image)
    #     qpainter.end()

    def set_scene_image(self, scene_image):
        if not is_ready():
            logger.warning("Projector is not ready!")
            return
        else:
            self.scene_image = scene_image
            out_image = util.get_qimage_from_np_image(scene_image)
            # out_image = out_image.mirrored(horizontal=True, vertical=False)
            self.setPixmap(QPixmap.fromImage(out_image))
            # self.setScaledContents(True)
            # self.update()

            # self.setMinimumSize(self.image.size())
            self.update()


class ProjectorService(Service):
    def __init__(self, service_name, screen_id=0):
        super().__init__(service_name)
        init_projector(screen_id)
        left, top, width, height = get_projector_geometry()
        self.projector_view = ProjectorView(top, left, Frame(width, height))
        self.projector_view.move(left, top)
        self.projector_view.resize(width, height)
        self.projector_view.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        self.projector_view.showFullScreen()

        from isar.services.servicemanager import ServiceNames
        self.camera_service = servicemanager.get_service(ServiceNames.CAMERA1)
        self.camera_service.start_capture()

        self.scenes_model = ScenesModel()
        self._stop_event = multiprocessing.Event()
        self.projector_process: multiprocessing.Process = None

        self.projector_needs_calibration = True

    def start(self):
        # while True:
        #     camera_frame = self.camera_service.get_frame()
        #     cv2.imshow("isar", camera_frame.raw_image)
        #     if cv2.waitKey(50) > 0:
        #         cv2.destroyAllWindows()
        #         break

        self.projector_process = multiprocessing.Process(target=self._start_service)
        self.projector_process.daemon = True
        self.projector_process.start()

    def _start_service(self):
        while not self._stop_event.is_set():
            if self.projector_needs_calibration:
                time.sleep(1)
                self.calibrate_projector()
                self.projector_needs_calibration = False
                time.sleep(10)

            time.sleep(0.05)
            self.update_projector_view()
            time.sleep(0.05)

    def calibrate_projector(self):
        pattern_size, chessboard_img = create_chessboard_image(self.projector_view.scene_size)
        self.projector_view.set_scene_image(chessboard_img)
        # if self.camera_service:
        #     camera_frame = self.camera_service.get_frame()
        #     cv2.imshow("isar", camera_frame.raw_image)
        #     cv2.waitKey(50)

    def update_projector_view(self):
        # TODO: prepare projector image from the scene annotation and
        #  result from object detection

        dummy_scene_image = create_dummy_scene_image(self.projector_view.scene_size)
        self.projector_view.set_scene_image(dummy_scene_image)

    def stop(self):
        self._stop_event.set()
        self.projector_process.terminate()
        self.projector_process.join()


def create_chessboard_image(scene_size):
    logger.info("Create chessboard image.")
    scene_width, scene_height = scene_size
    center = int(scene_width/2), int(scene_height/2)
    square_size = 50
    chessboard_width, chessboard_height = 10 * square_size, 7 * square_size

    chessboard = np.ones((chessboard_height, chessboard_width, 3), np.uint8)
    chessboard.fill(255)
    image = np.ones((scene_height, scene_width, 3), np.uint8)
    image.fill(255)

    xs = np.arange(0, chessboard_width, square_size)
    ys = np.arange(0, chessboard_height, square_size)

    for j, y in enumerate(ys):
        for i, x in enumerate(xs):
            if (i + j) % 2 == 0:
                chessboard[y:y + square_size, x:x + square_size] = (0, 0, 0)
    cv2.imwrite("tmp/tmp_files/chessboard.jpg", chessboard)

    x, y = center[0] - int(chessboard_width / 2), center[1] - int(chessboard_height/2)
    image[y:y+chessboard_height, x:x+chessboard_width] = chessboard
    cv2.imwrite("tmp/tmp_files/projector_calibration_image.jpg", image)

    return (len(ys) - 1, len(xs) - 1), image


def create_dummy_scene_image(scene_size):
    width, height = scene_size
    # scene_image = np.zeros((height, width, 3), np.uint8)
    scene_image = np.ones((height, width, 3), np.uint8)
    scene_image[:] = (0, 255, 255)

    # scene_image = cv2.cvtColor(scene_image, cv2.COLOR_BGR2BGRA)
    scene_image = cv2.rectangle(scene_image, (100, 100), (width - 100, height - 100), (0, 255, 0), 10)
    return scene_image
