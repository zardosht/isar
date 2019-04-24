import logging

import numpy as np
import cv2


logger = logging.getLogger("isar.projection.util")

debug = True


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
    if debug: cv2.imwrite("tmp/tmp_files/chessboard.jpg", chessboard)

    x, y = center[0] - int(chessboard_width / 2), center[1] - int(chessboard_height/2)
    image[y:y+chessboard_height, x:x+chessboard_width] = chessboard
    if debug: cv2.imwrite("tmp/tmp_files/projector_calibration_image.jpg", image)

    return (len(ys) - 1, len(xs) - 1), image


def create_dummy_scene_image(projector_width, projector_height, scene_rect):
    # TODO: This some how needs rework. Define a scene_size attribute for the scene.
    # TODO: The tabel scene_size will be defined using markers. Then you only need to render all
    # dummy_scene_image = np.zero((height, width, 3), np.uint8)
    width, height = scene_rect[2], scene_rect[3]
    dummy_scene_image = create_empty_image((projector_width, projector_height), (0, 0, 255))

    vertex1 = (scene_rect[0], scene_rect[1])
    vertex2 = (scene_rect[0] + width, scene_rect[1] + height)
    # dummy_scene_image = cv2.cvtColor(dummy_scene_image, cv2.COLOR_BGR2BGRA)
    dummy_scene_image = cv2.rectangle(dummy_scene_image, vertex1, vertex2, (0, 255, 0), 5)
    if debug: cv2.imwrite("tmp/tmp_files/dummy_scene_image.jpg", dummy_scene_image)
    return dummy_scene_image


def create_empty_image(size, color):
    empty_image = np.ones((size[1], size[0], 3), np.uint8)
    empty_image[:] = color
    return empty_image


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



