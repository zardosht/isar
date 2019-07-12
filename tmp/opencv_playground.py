import glob
import os
import time
import traceback

import cv2
import numpy as np
from screeninfo import get_monitors


def f1():
    height, width = 100, 200
    image = np.zeros((height, width, 4), np.uint)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2BGRA)

    # image[np.all(image == [0, 0, 0, 255], axis=2)] = [0, 0, 0, 0]

    image.fill(255)
    image[np.all(image == [255, 255, 255, 255], axis=2)] = [255, 255, 255, 0]

    cv2.imwrite("tmp_files/tmp_img.png", image)


def f2():
    # width, height = 1000, 700
    width, height = 1280, 800
    # width, height = 1280, 700
    # width, height = 1200, 700
    # width, height = 1200, 800
    # width, height = 1280, 820
    # width, height = 1200, 820
    # width, height = 1100, 700

    image = np.ones((height, width, 3), np.uint8)
    image.fill(255)

    square_size = 100
    xs = np.arange(0, width, square_size)
    ys = np.arange(0, height, square_size)

    for j, y in enumerate(ys):
        for i, x in enumerate(xs):
            if (i + j) % 2 == 0:
                image[y:y + square_size, x:x + square_size] = (0, 0, 0)
                cv2.imwrite("tmp_files/chessboard.jpg", image)


def f3():
    # prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
    objp = np.zeros((6 * 7, 3), np.float32)
    objp[:, :2] = np.mgrid[0:7, 0:6].T.reshape(-1, 2)
    print(objp)

    # objp = np.zeros((2*3, 3), np.float32)
    # print(objp)
    # print("--------------------")
    # print(objp[:, :2])
    # print("--------------------")
    # print(np.mgrid[0:3, 0:2])
    # print("--------------------")
    # print(np.mgrid[0:3, 0:2].T)
    # print("--------------------")
    # print(np.mgrid[0:3, 0:2].T.reshape(-1, 2))
    # print("--------------------")
    #
    # objp[:, :2] = np.mgrid[0:3, 0:2].T.reshape(-1, 2)
    # print(objp)


def f4():
    # x = np.array([1, 2, 3])
    x = np.array([0, 1, 2])

    # y = np.array([10, 20, 30, 40])
    y = np.array([0, 1])
    # y = np.array([10, 20, 30])

    # YY, XX = np.meshgrid(y, x)
    XX, YY = np.meshgrid(x, y)
    AA, BB = np.mgrid[0:3, 0:2]

    print(XX, "\n-------------\n", YY)
    print("-------------------------")
    print(AA, "\n-------------\n", BB)


def f5():
    # termination criteria
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

    # prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
    objp = np.zeros((6 * 7, 3), np.float32)
    objp[:, :2] = np.mgrid[0:7, 0:6].T.reshape(-1, 2)

    # Arrays to store object points and image points from all the images.
    objpoints = []  # 3d point in real world space
    imgpoints = []  # 2d points in image plane.

    # img = cv2.imread("tmp_files/chessboard.jpg")
    # img = cv2.imread("tmp_files/projector_calibration_image.jpg")
    img = cv2.imread("tmp_files/tmp_image.jpg")
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Find the chess board corners
    pattern = (9, 6)
    ret, corners = cv2.findChessboardCorners(gray, pattern, None)

    # If found, add object points, image points (after refining them)
    if ret == True:
        objpoints.append(objp)

        corners2 = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
        imgpoints.append(corners2)

        # Draw and display the corners
        pattern = (9, 6)
        img = cv2.drawChessboardCorners(img, pattern, corners2, ret)

        cv2.namedWindow("img", cv2.WINDOW_GUI_NORMAL)
        cv2.imshow('img', img)
        cv2.waitKey()

    cv2.destroyAllWindows()


def f6():
    monitors = get_monitors("osx")
    for m in monitors:
        print(str(m))

    screen_id = 1
    screen = monitors[screen_id]
    offset_x = int(screen.x)
    offset_y = 0

    width = int(screen.width)
    height = int(screen.height)

    # cv2.namedWindow("projector", cv2.WND_PROP_FULLSCREEN)
    # cv2.setWindowProperty("projector", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    # cv2.moveWindow("projector", offset_x, offset_y)

    # cv2.namedWindow("projector", cv2.WINDOW_GUI_NORMAL)
    # cv2.moveWindow("projector", offset_x, offset_y)
    # cv2.namedWindow("projector", cv2.WINDOW_NORMAL)
    # cv2.namedWindow("projector", cv2.WINDOW_FULLSCREEN)
    #cv2.setWindowProperty("projector", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    window_name = 'projector'
    # cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.namedWindow(window_name, cv2.WINDOW_GUI_NORMAL)
    cv2.moveWindow(window_name, int(screen.x) - 1, int(screen.y) - 1)

    blank_image = np.ones((height, width, 3), np.uint8)
    blank_image[:] = (255, 0, 255)
    cv2.imshow("projector", blank_image)

    time.sleep(5)

    cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    # blank_image = np.ones((height, width, 3), np.uint8)
    # blank_image[:] = (255, 0, 255)
    cv2.imshow("projector", blank_image)
    cv2.waitKey(30000)


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
        pattern = (9, 6)
        chessboard_with_corners = cv2.drawChessboardCorners(img, pattern, corners2, ret)

        cv2.namedWindow(window_name, cv2.WINDOW_GUI_NORMAL)
        cv2.imshow(window_name, chessboard_with_corners)

    return np.array(chessboard_points).squeeze()


def compute_new_position(position, homography):
    try:
        # homogenous_position = np.array((position[0], position[1], 1)).reshape((3, 1))
        # transformed_position = np.dot(homography, homogenous_position)
        # transformed_position = np.sum(transformed_position, 1)
        # new_x = int(round(transformed_position[0] / transformed_position[2]))
        # new_y = int(round(transformed_position[1] / transformed_position[2]))

        homogenous_position = np.array((position[0], position[1], 1)).reshape((3, 1))
        new_position = np.dot(homography, homogenous_position)
        new_x = new_position[0]
        new_y = new_position[1]

        return new_x, new_y

    except Exception as err :
        print("Exception in transforming new annotation position. Homography: %s", homography)
        traceback.print_exc()
        return position


def f7():
    # termination criteria

    # prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
    objp = np.zeros((6 * 7, 3), np.float32)
    objp[:, :2] = np.mgrid[0:7, 0:6].T.reshape(-1, 2)

    projector_img = cv2.imread("tmp_files/projector_calibration_image.jpg")
    projector_img = cv2.flip(projector_img, -1)
    projector_points = get_chessboard_points("projector_points", projector_img)

    camera_img = cv2.imread("tmp_files/tmp_image.jpg")
    # camera_img = cv2.flip(camera_img, -1)
    camera_points = get_chessboard_points("camera_points", camera_img)

    print("Projector Points: shape " + str(projector_points.shape))
    print("---------------------------")
    print(projector_points)

    print(" ")
    print("Camera Points: shape " + str(camera_points.shape))
    print("---------------------------")
    print(camera_points)

    # cv2.waitKey()

    print(" ")
    print("Homography: ")
    print("---------------------------")
    # homography_matrix, status = cv2.findHomography(camera_points, projector_points, cv2.RANSAC, 5.0)
    homography_matrix, status = cv2.findHomography(projector_points, camera_points, cv2.RANSAC, 3)
    print(homography_matrix)

    source = cv2.imread("tmp_files/projector_calibration_image.jpg")
    p1 = (388, 225)
    p2 = (888, 573)
    source = cv2.line(source, p1, p2, (0, 0, 255), 8)
    cv2.imshow("source", source)

    dest = cv2.imread("tmp_files/calibration_image_on_table.jpg")
    source_warpped = cv2.warpPerspective(source, homography_matrix, (dest.shape[1], dest.shape[0]))
    cv2.imshow("source_warpped", source_warpped)

    warpped_p1 = compute_new_position(p1, homography_matrix)
    warpped_p2 = compute_new_position(p2, homography_matrix)
    dest = cv2.line(dest, warpped_p1, warpped_p2, (0, 0, 255), 8)
    dest = cv2.resize(dest, (source.shape[1], source.shape[0]))
    cv2.imshow("dest_with_line", dest)

    cv2.waitKey()

    cv2.destroyAllWindows()


def create_empty_image(size, color):
    empty_image = np.ones((size[1], size[0], 3), np.uint8)
    empty_image[:] = color
    return empty_image


def f8():
    image = create_empty_image((500, 500), (255, 255, 255))
    text = "Text"
    font_scale = 0.5
    text_color = (255, 0, 0)
    text_thickness = 1

    text_position = (50, 50)
    font = cv2.FONT_HERSHEY_SIMPLEX
    line_type = cv2.LINE_AA

    cv2.putText(image,
                text,
                text_position,
                font,
                font_scale,
                text_color,
                text_thickness,
                line_type)

    cv2.line(image, (50, 50), (50, 100), (0, 255, 0))

    cv2.imshow("text", image)
    cv2.waitKey()
    cv2.destroyAllWindows()


def f9():
    fpss = []
    if os.name == "posix":
        cam_id = 0
        _capture = cv2.VideoCapture(cam_id, cv2.CAP_V4L2)
        # _capture = cv2.VideoCapture(cam_id)

        width = 1920
        height = 1080
        capture_fps = 24
        _capture.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
        _capture.set(cv2.CAP_PROP_FPS, capture_fps);
        _capture.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        _capture.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        # _capture.set(cv2.CAP_PROP_CONVERT_RGB, False)

        while True:
            start = time.time()
            ret, frame = _capture.read()
            if ret:
                duration = time.time() - start
                fps = 1 / duration
                fpss.append(fps)

                cv2.imshow("camera", frame)
                key = cv2.waitKey(1)
                if key & 0xFF == ord('q'):
                    break

        print("Average FPS: ", sum(fpss) / len(fpss))
        _capture.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    # f2()
    # f3()
    # f4()
    # f5()
    # f6()
    # f7()
    # f8()
    f9()

    # img = cv2.imread("tmp_files/tmp_image.jpg")
    # cv2.imshow("tmp_package", img)
    # cv2.waitKey()
    # cv2.destroyAllWindows()


