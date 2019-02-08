import logging
import threading
import traceback

import cv2
import numpy as np
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import Qt, QPoint

from isar.camera.camera import CameraService, CameraFrame
from isar.scene.util import Frame

logger = logging.getLogger("isar.projection.projector")

debug = True


class QtCore(object):
    pass


class ProjectorView(QtWidgets.QWidget):
    def __init__(self, parent, screen_id, camera_service):
        super().__init__(parent)
        self.projector = None
        self.width = 0
        self.height = 0
        self.scene_size = None
        self.calibrating = False

        self.image = None
        self.homography_matrix = np.identity(3, dtype=np.float64)
        self.camera_service: CameraService = camera_service

        self.init_projector(screen_id)

        self.move(self.projector.left(), self.projector.top())
        self.resize(self.projector.width(), self.projector.height())
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.showFullScreen()

    def set_scene_image(self, scene_image):
        if self.calibrating:
            if debug: cv2.imwrite("tmp/tmp_files/calibration_image.jpg", scene_image)
            scene_image = cv2.resize(scene_image, (self.width, self.height))
        else:
            if debug: cv2.imwrite("tmp/tmp_files/scene_image.jpg", scene_image)
            scene_image = cv2.warpPerspective(scene_image, self.homography_matrix, (self.width, self.height))
            if debug: cv2.imwrite("tmp/tmp_files/scene_image_warpped.jpg", scene_image)

        height, width, bpc = scene_image.shape
        bpl = bpc * width
        self.image = QtGui.QImage(scene_image.data, width, height, bpl, QtGui.QImage.Format_RGB888)
        self.setMinimumSize(self.image.size())
        logger.debug("Image size: %s", self.image.size())
        self.update()

    def init_projector(self, screen_id):
        self.projector = QtWidgets.QApplication.desktop().screenGeometry(screen_id)
        self.width = int(self.projector.width())
        self.height = int(self.projector.height())
        self.scene_size = Frame(self.width, self.height)

        blank_image = np.ones((self.height, self.width, 3), np.uint8)
        blank_image[:] = (255, 0, 255)

        self.set_scene_image(blank_image)

    def paintEvent(self, event):
        qpainter = QtGui.QPainter()
        qpainter.begin(self)
        if self.image:
            qpainter.drawImage(QPoint(0, 0), self.image)
        qpainter.end()

    def calibrate_projector(self):
        self.calibrating = True
        pattern_size, chessboard_img = create_chessboard_image(self.scene_size)
        self.set_scene_image(chessboard_img)
        t = threading.Thread(target=self.calibrate, args=(chessboard_img, ))
        t.start()

    def calibrate(self, projector_img):
        self.camera_service.start_capture()
        max_iterations = 100
        iter = 0
        found_homography = False
        while not found_homography:
            try:
                projector_img = cv2.flip(projector_img, -1)
                projector_points = get_chessboard_points("projector_points", projector_img)

                camera_frame: CameraFrame = self.camera_service.get_frame()
                camera_img = camera_frame.raw_image
                camera_img = cv2.resize(camera_img, self.scene_size)
                # camera_img = cv2.flip(camera_img, -1)

                if debug: cv2.imwrite("tmp/tmp_files/calibration_image_on_table.jpg", camera_img)

                camera_points = get_chessboard_points("camera_points", camera_img)

                if projector_points.shape != camera_points.shape:
                    logger.warning("Finding homography: projector_points and camera_points don't have the same shape!")
                    continue

                self.homography_matrix, mask = cv2.findHomography(camera_points, projector_points, cv2.RANSAC, 3)
                # self.homography_matrix, mask = cv2.findHomography(projector_points, camera_points, cv2.RANSAC, 3)
                logger.info("Homography matrix: " + str(self.homography_matrix))

                if np.all(mask):
                    logger.info("Found good homography. All mask elements are 1. Break.")
                    found_homography = True

                iter += 1
                if iter > max_iterations:
                    found_homography = True

            except Exception as exp:
                logger.error("Error finding homography: ", str(exp))
                traceback.print_tb(exp.__traceback__)

        self.calibrating = False

    def update_projector_view(self):
        # TODO: prepare projector image from the scene annotation and
        #  result from object detection

        camera_img = self.camera_service.get_frame().raw_image
        if debug: cv2.imwrite("tmp/tmp_files/what_camera_sees_on_table.jpg", camera_img)

        # dummy_scene_image = create_dummy_scene_image(self.scene_size)
        # dummy_scene_image_warpped = dummy_scene_image

        # dummy_scene_image = create_dummy_scene_image(self.camera_service.get_camera_capture_size())
        # dummy_scene_image_warpped = cv2.warpPerspective(dummy_scene_image, self.homography_matrix, self.scene_size)

        dummy_scene_image = create_dummy_scene_image(self.scene_size)
        dummy_scene_image_warpped = cv2.warpPerspective(dummy_scene_image, self.homography_matrix, self.scene_size)

        if debug: cv2.imwrite("tmp/tmp_files/dummy_scene_image_warpped.jpg", dummy_scene_image_warpped)

        return self.set_scene_image(dummy_scene_image_warpped)


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


def get_chessboard_points(window_name, img):
    chessboard_points = []  # 2d points in image plane.

    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Find the chess board corners
    pattern = (9, 6)
    ret, corners = cv2.findChessboardCorners(gray_img, pattern, None)

    # If found, add object points, image points (after refining them)
    if ret:
        corners2 = cv2.cornerSubPix(gray_img, corners, (11, 11), (-1, -1), criteria)
        chessboard_points.append(corners2)
        # Draw and display the corners
        # pattern = (9, 6)
        # chessboard_with_corners = cv2.drawChessboardCorners(img, pattern, corners2, ret)
        # cv2.namedWindow(window_name, cv2.WINDOW_GUI_NORMAL)
        # cv2.imshow(window_name, chessboard_with_corners)

    return np.array(chessboard_points).squeeze()