import logging
import multiprocessing
import threading
import time

import cv2
import numpy as np
from pylab import array, uint8
from screeninfo import get_monitors
from isar.scene import util
from isar.scene.scenemodel import ScenesModel
from isar.scene.util import Frame
from isar.services.service import Service

logger = logging.getLogger("isar.projection.projector")


class ProjectorView:
    def __init__(self):
        super().__init__()
        self.offset_x = 0
        self.offset_y = 0
        self.width = 0
        self.height = 0
        self.scene_size = None
        self.scene_image = None
        self.calibration_matrix = np.identity(3, dtype=np.float64)

    def set_scene_image(self, scene_image):
        self.scene_image = scene_image
        cv2.imshow("projector", scene_image)
        return cv2.waitKey(1)

    def init_projector(self, screen_id):
        monitors = get_monitors("osx")
        for m in monitors:
            print(str(m))

        self.screen = monitors[screen_id]
        self.offset_x = int(self.screen.x)
        self.offset_y = 0
        self.width = int(self.screen.width)
        self.height = int(self.screen.height)
        self.scene_size = Frame(self.width, self.height)

        cv2.namedWindow("projector", cv2.WINDOW_GUI_NORMAL)
        cv2.moveWindow("projector", self.offset_x, self.offset_y)

        # TODO: There is a bug in OpenCV fullscreen on macOS
        # cv2.setWindowProperty("projector", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

        blank_image = np.ones((self.height, self.width, 3), np.uint8)
        blank_image[:] = (255, 0, 255)
        cv2.imshow("projector", blank_image)
        cv2.waitKey(1000)

    def calibrate_projector(self):
        pattern_size, chessboard_img = create_chessboard_image(self.scene_size)
        return self.set_scene_image(chessboard_img)

    def update_projector_view(self):
        # TODO: prepare projector image from the scene annotation and
        #  result from object detection

        dummy_scene_image = create_dummy_scene_image(self.scene_size)
        return self.set_scene_image(dummy_scene_image)


class ProjectorService(Service):
    def __init__(self, service_name, screen_id=0):
        super().__init__(service_name)
        self.screen_id = screen_id
        self.projector_view = ProjectorView()
        self.projector_needs_calibration = True

        self.scenes_model = ScenesModel()
        self._stop_event = multiprocessing.Event()

    def start(self):
        self.projector_view.init_projector(self.screen_id)
        while not self._stop_event.is_set():
            if self.projector_needs_calibration:
                time.sleep(1)
                ret = self.projector_view.calibrate_projector()
                if ret > 0:
                    break

                self.projector_needs_calibration = False
                time.sleep(10)

            ret = self.projector_view.update_projector_view()
            if ret > 0:
                break

            time.sleep(0.005)

    def stop(self):
        self._stop_event.set()
        cv2.destroyAllWindows()


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
