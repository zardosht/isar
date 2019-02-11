import logging
import math
import threading
import time
import traceback

import cv2
import numpy as np
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import Qt, QPoint

from isar.camera.camera import CameraService, CameraFrame
from isar.scene.util import Frame

logger = logging.getLogger("isar.projection.projector")

debug = False


aruco_dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)


class ProjectorView(QtWidgets.QWidget):
    def __init__(self, parent, screen_id, camera_service):
        super().__init__(parent)
        self.projector = None
        self.projector_width = 0
        self.projector_height = 0
        self.scene_size = None
        self.scene_rect = None
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
        if scene_image is None:
            logger.warning("scene_image is None!")
            return

        if self.calibrating:
            if debug: cv2.imwrite("tmp/tmp_files/calibration_image.jpg", scene_image)
            scene_image_warpped = scene_image
        else:
            if debug: cv2.imwrite("tmp/tmp_files/scene_image.jpg", scene_image)
            scene_image_warpped = scene_image

        height, width, bpc = scene_image_warpped.shape
        bpl = bpc * width
        self.image = QtGui.QImage(scene_image_warpped.data, width, height, bpl, QtGui.QImage.Format_RGB888)
        self.setMinimumSize(self.image.size())
        logger.debug("Image size: %s", self.image.size())
        self.update()

    def init_projector(self, screen_id):
        self.projector = QtWidgets.QApplication.desktop().screenGeometry(screen_id)
        self.projector_width = int(self.projector.width())
        self.projector_height = int(self.projector.height())

        blank_image = np.ones((self.projector_height, self.projector_width, 3), np.uint8)
        blank_image[:] = (255, 0, 255)

        self.set_scene_image(blank_image)

    def paintEvent(self, event):
        qpainter = QtGui.QPainter()
        qpainter.begin(self)
        if self.image:
            # put the image at the center of widget
            w, h = event.rect().width(), event.rect().height()
            x = (w - self.image.size().width()) / 2
            y = (h - self.image.size().height()) / 2
            qpainter.drawImage(QPoint(x, y), self.image)
        qpainter.end()

    def calibrate_projector(self):
        # We don't need a 3D camera-projector calibration
        # (which would require
        #     * calibrating the camera sparately (using for examle a chessboard),
        #     * then projecting a known pattern and calibrating the projector using camera image of that known pattern
        #           [this works because we now know the parameters (including position and orientation) of the camera]
        # )  see http://www.morethantechnical.com/2017/11/17/projector-camera-calibration-the-easy-way/
        #
        # What we need is a simple mapping between camera points and projector points.
        # Why?
        #    because we assume the projector points are the same as the 3D real world points. That is there
        #       is no need to extra calibrate projector (know its parameters and position and orientation with regard to
        #       3D real world)
        # We make sure the keystone correction is adjusted on the projector (to get rid of perspective keystone effect)
        # What we want now is to know if the camera says
        #       "the bounding box of the hammer is position (10, 10) to (80, 200)",
        #       what would those camera-space coordinates be in projector-space coordinates
        # This can be achieved by a simple homography between camera and the projector.
        # We use a chessboard pattern for calibration.
        # The projector projects the chess board (known pattern)
        # The camera sees the chessboard and correspondence points are found (chessboard corners)
        # After that homography is found, we check it by projecting circles on "reprojected chessboard corners".
        #       That is, we take the chessboard corners from camera image,
        #                we re-calculate (reproject) them to projector-space by multiplying them with the homography.
        #                we draw circles on the scene_image at the resulted (now projector-space) coordinates
        #                the discrepancy of those circles with the chessboard corners in the projected image on the
        #                table show how far our homography is estimating.

        self.calibrating = True
        pattern_size, chessboard_img = create_chessboard_image(self.projector_width, self.projector_height)
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
                # projector_img = cv2.flip(projector_img, -1)
                projector_points = get_chessboard_points("projector_points", projector_img)

                camera_frame: CameraFrame = self.camera_service.get_frame()
                camera_img = camera_frame.raw_image
                # camera_img = cv2.resize(camera_img, self.scene_size)
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

        # testing the found homography
        camera_frame: CameraFrame = self.camera_service.get_frame()
        camera_img = camera_frame.raw_image
        if debug: cv2.imwrite("tmp/tmp_files/what_camera_sees_on_table.jpg", camera_img)
        # camera_img = cv2.resize(camera_img, self.scene_size)

        camera_points = get_chessboard_points("camera_points", camera_img)
        reprojected_points = cv2.perspectiveTransform(np.array([camera_points]), self.homography_matrix)
        reprojected_points = reprojected_points.squeeze()
        test_chessboard_image = projector_img.copy()
        for reprojected_point in reprojected_points:
            cv2.circle(test_chessboard_image, tuple(reprojected_point), 5, (0, 0, 255), 2)

        self.set_scene_image(test_chessboard_image)
        time.sleep(10)

        # Detect the scene border markers and get the scene boudaries from them.
        # All scene images must be resized to scene boundaries and shown in the center of projector widget
        marker_corners, marker_ids, _ = cv2.aruco.detectMarkers(camera_img, aruco_dictionary)
        if len(marker_corners) != 2 :
            logger.warning("Error detecting the scene corners. Not all four markers were detected. return.")
            return

        # compute scene rect in projector-space
        self.scene_rect = compute_scene_rect(marker_corners, marker_ids, self.homography_matrix)
        self.scene_size = (self.scene_rect[1], self.scene_rect[2])

        # calibration finished
        self.calibrating = False

    def update_projector_view(self):
        # TODO: draw all the annotations on the scene_image
        scene_image = create_dummy_scene_image(self.projector_width,
                                               self.projector_height,
                                               self.scene_rect)
        if debug: cv2.imwrite("tmp/tmp_files/dummy_scene_image.jpg", scene_image)
        self.set_scene_image(scene_image)


def compute_scene_rect(marker_corners, marker_ids, cam_proj_homography):
    # marker corners are in clock-wise order
    # there are only two markers. So, one has index 0, the other has index 1,
    # however we don't know which one is marker 0 (the top-left marker)
    top_left_marker_index = 0
    for idx, marker_id in enumerate(marker_ids):
        if marker_id == 0:
            top_left_marker_index = idx

    vertex1_marker = marker_corners[top_left_marker_index].reshape(4, 2)
    vertex2_marker = marker_corners[1 - top_left_marker_index].reshape(4, 2)

    c_v1 = (vertex1_marker[0][0], vertex1_marker[0][1])
    c_v2 = (vertex2_marker[2][0], vertex2_marker[2][1])

    proj_points = cv2.perspectiveTransform(np.array([[c_v1, c_v2]]), cam_proj_homography)
    proj_points = proj_points.squeeze()
    p_v1 = proj_points[0]
    p_v2 = proj_points[1]

    width, height = (abs(p_v1[0] - p_v2[0]), abs(p_v1[1] - p_v2[1]))
    return int(p_v1[0]), int(p_v1[1]), int(width), int(height)


def create_chessboard_image(width, height):
    logger.info("Create chessboard image.")
    center = int(width/2), int(height/2)
    square_size = 50
    chessboard_width, chessboard_height = 10 * square_size, 7 * square_size

    chessboard = np.ones((chessboard_height, chessboard_width, 3), np.uint8)
    chessboard.fill(255)
    image = np.ones((height, width, 3), np.uint8)
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


def create_dummy_scene_image(projector_width, projector_height, scene_rect):
    # dummy_scene_image = np.zero((height, width, 3), np.uint8)
    width, height = scene_rect[2], scene_rect[3]
    dummy_scene_image = np.ones((projector_height, projector_width, 3), np.uint8)
    dummy_scene_image[:] = (0, 255, 255)

    vertex1 = (scene_rect[0], scene_rect[1])
    vertex2 = (scene_rect[0] + width, scene_rect[1] + height)
    # dummy_scene_image = cv2.cvtColor(dummy_scene_image, cv2.COLOR_BGR2BGRA)
    dummy_scene_image = cv2.rectangle(dummy_scene_image, vertex1, vertex2, (0, 255, 0), 10)
    if debug: cv2.imwrite("tmp/tmp_files/dummy_scene_image.jpg", dummy_scene_image)
    return dummy_scene_image


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