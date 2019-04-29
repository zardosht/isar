import logging
import math
import threading
import time
import traceback

import cv2
import numpy as np
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import Qt, QPoint

import isar
from isar.camera.camera import CameraService, CameraFrame
from isar.projection import projectionutil
from isar.scene import sceneutil
from isar.scene.scenemodel import current_project
from isar.scene.scenerenderer import SceneRenderer
from isar.scene.sceneutil import get_scene_scale_factor
from isar.services import servicemanager
from isar.services.servicemanager import ServiceNames

logger = logging.getLogger("isar.projection.projector")

debug = False


class ProjectorView(QtWidgets.QWidget):
    def __init__(self, parent, screen_id, camera_service):
        super().__init__(parent)
        self.__annotations_model = None
        self.projector = None
        self.projector_width = 0
        self.projector_height = 0
        self.calibrating = False

        self.scene_rect_c = None
        self.scene_size_p = None
        self.scene_rect_p = None
        self.scene_homography = None
        self.scene_scale_factor_c = None
        self.scene_size_p_initialized = False

        self.image = None
        self.homography_matrix = np.identity(3, dtype=np.float64)
        self.camera_service: CameraService = camera_service

        self.init_projector(screen_id)

        self.move(self.projector.left(), self.projector.top())
        self.resize(self.projector.width(), self.projector.height())
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.showFullScreen()

        self.__annotations_model = None
        self.__physical_objects_model = None
        self.scene_renderer = SceneRenderer()
        self.scene_renderer.set_annotations_model(self.__annotations_model)
        self.scene_renderer.set_physical_objects_model(self.__physical_objects_model)

    def set_annotations_model(self, annotations_model):
        self.__annotations_model = annotations_model
        self.scene_renderer.set_annotations_model(self.__annotations_model)

    def set_physical_objects_model(self, phm):
        self.__physical_objects_model = phm
        self.scene_renderer.set_physical_objects_model(self.__physical_objects_model)

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
        pattern_size, chessboard_img = projectionutil.create_chessboard_image(self.projector_width, self.projector_height)
        self.set_scene_image(chessboard_img)
        t_calib = threading.Thread(target=self.calibrate, args=(chessboard_img,))
        t_calib.start()

    def calibrate(self, projector_img):
        self.camera_service.start_capture()
        max_iterations = 100
        iter = 0
        found_homography = False
        while not found_homography:
            try:
                # projector_img = cv2.flip(projector_img, -1)
                projector_points = projectionutil.get_chessboard_points("projector_points", projector_img)

                camera_frame: CameraFrame = self.camera_service.get_frame()
                camera_img = camera_frame.raw_image
                # camera_img = cv2.resize(camera_img, self.scene_size)
                # camera_img = cv2.flip(camera_img, -1)

                if debug: cv2.imwrite("tmp/tmp_files/calibration_image_on_table.jpg", camera_img)

                camera_points = projectionutil.get_chessboard_points("camera_points", camera_img)

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

        camera_points = projectionutil.get_chessboard_points("camera_points", camera_img)
        reprojected_points = cv2.perspectiveTransform(np.array([camera_points]), self.homography_matrix)
        reprojected_points = reprojected_points.squeeze()
        test_chessboard_image = projector_img.copy()
        for reprojected_point in reprojected_points:
            cv2.circle(test_chessboard_image, tuple(reprojected_point), 5, (0, 0, 255), 2)

        self.set_scene_image(test_chessboard_image)
        time.sleep(5)

        # calibration finished
        self.calibrating = False

    def init_scene_size(self):
        if self.homography_matrix is None:
            logger.warning("Homography matrix is None. Cannot calculate scene size.")
            return

        max_iter = 100
        num_iter = -1
        while True:
            num_iter += 1
            camera_frame = self.camera_service.get_frame()
            if camera_frame is None:
                # logger.error("camera_frame is None")
                continue

            # compute scene rect in projector-space
            scene_rect_c, scene_rect_p, scene_homography = sceneutil.compute_scene_rect(camera_frame, self.homography_matrix)
            if scene_rect_p is None and num_iter < max_iter:
                continue
            elif scene_rect_p is not None:
                self.scene_rect_c = scene_rect_c
                self.scene_rect_p = scene_rect_p
                self.scene_size_p = (self.scene_rect_p[2], self.scene_rect_p[3])
                self.scene_homography = scene_homography
                self.scene_scale_factor_c = sceneutil.get_scene_scale_factor(camera_frame.raw_image.shape, self.scene_rect_c)
                self.scene_size_p_initialized = True

                sceneutil.scene_rect_c = self.scene_rect_c
                sceneutil.scene_rect_p = self.scene_rect_p
                sceneutil.scene_scale_factor_c = self.scene_scale_factor_c

                logger.info("Scene size initialized successfully!")
                break
            else:
                logger.warning("Could no calculate scene size.")
                break

    def update_projector_view(self, camera_frame):
        # TODO: draw all the annotations on the scene_image

        # first of course we need to load the project (in domainlearning)

        #  create an empty scene image
        #  check how you can use the annoation tools for drawing on it.
        #  of course everything must be in projector coordinates and scaled to scene_size / scene_rect

        if not self.scene_size_p_initialized:
            logger.warning("Projector scene size is not initialized. Return!")
            return

        # camera_frame: CameraFrame = self.camera_service.get_frame()
        camera_img = camera_frame.raw_image
        if debug: cv2.imwrite("tmp/tmp_files/what_camera_sees_on_table.jpg", camera_img)

        scene_image = projectionutil.create_dummy_scene_image(self.projector_width,
                                                              self.projector_height,
                                                              self.scene_rect_p)

        srect_x_p, srect_y_p, srect_width_p, srect_height_p = self.scene_rect_p

        scene_size_c = (self.projector_width, self.projector_height)
        current_project = isar.scene.scenemodel.current_project
        if current_project is not None:
            scene_size_c = current_project.scene_size

        self.scene_renderer.scene_rect = self.scene_rect_c
        self.scene_renderer.scene_scale_factor = self.scene_scale_factor_c
        self.scene_renderer.opencv_img = sceneutil.create_empty_image(scene_size_c, (255, 255, 255))

        self.scene_renderer.draw_scene_physical_objects()
        self.scene_renderer.draw_scene_annotations()

        # =========== experimental =============
        selection_stick_service = servicemanager.get_service(ServiceNames.SELECTION_STICK)
        selection_stick_service.draw_current_rect(self.scene_renderer.opencv_img, self.homography_matrix, self.scene_homography)
        # ======================================

        scene_renderer_opencv_img_warpped = cv2.resize(self.scene_renderer.opencv_img, (srect_width_p, srect_height_p))

        # scene_renderer_opencv_img_warpped = \
        #     cv2.warpPerspective(self.scene_renderer.opencv_img, self.scene_homography, (srect_width_p, srect_height_p))

        if debug: cv2.imwrite("tmp/tmp_files/scene_renderer_opencv_img_warpped.jpg", scene_renderer_opencv_img_warpped)

        end_index_y = min(srect_y_p + srect_height_p, scene_image.shape[0])
        end_index_x = min(srect_x_p + srect_width_p, scene_image.shape[1])

        if (end_index_y - srect_y_p) != scene_renderer_opencv_img_warpped.shape[0]:
            scene_renderer_opencv_img_warpped = scene_renderer_opencv_img_warpped[0:(end_index_y - srect_y_p)]

        scene_image[srect_y_p:end_index_y,
                    srect_x_p:end_index_x] = scene_renderer_opencv_img_warpped

        if debug: cv2.imwrite("tmp/tmp_files/dummy_scene_image.jpg", scene_image)
        self.set_scene_image(scene_image)



