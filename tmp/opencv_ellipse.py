import time

import cv2
import numpy as np

# Colors (B, G, R)
from isar.scene import sceneutil

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)


def create_blank(width, height, color=(0, 0, 0)):
    """Create new image(numpy array) filled with certain color in BGR"""
    image = np.zeros((height, width, 3), np.uint8)
    # Fill image with color
    image[:] = color

    return image


def draw_half_circle_rounded(image):
    height, width = image.shape[0:2]
    # Ellipse parameters
    radius = 100
    center = (int(width / 2), int(height / 2))
    axes = (radius, radius)
    angle = 0
    startAngle = 180
    endAngle = 360
    thickness = 10

    cv2.ellipse(image, center, axes, -90, 0, 355, BLACK, -1)


def draw_timer_as_chart():
    text = "Hello Timer"

    current_time = 0
    duration = 20
    font = cv2.FONT_HERSHEY_SIMPLEX
    line_type = cv2.LINE_AA
    font_scale = 0.5
    text_thickness = 2
    height, width = image.shape[0:2]
    position = (int(width / 2), int(height / 2))
    text_color = BLACK

    text_size, _ = cv2.getTextSize(str(duration), font, font_scale, text_thickness)
    radius = int(3 * text_size[1])

    width = 2 * radius + 2 * text_thickness
    height = 2 * radius + 2 * text_thickness
    chart_image = np.zeros((height, width, 3), np.uint8)
    chart_image[:] = (128, 128, 128)

    center = (int(width / 2), int(height / 2))
    # a circle for total duration
    cv2.ellipse(chart_image, center, (radius, radius), -90, 0, 360, (255, 0, 0), -1)
    cv2.imshow('timer as chart', image)
    cv2.waitKey(1)

    for i in range(duration + 1):
        current_time = i
        # a circle segment on top of that for current time
        end_angle = int(current_time * (360 / duration))
        cv2.ellipse(chart_image, center, (radius, radius), -90, 0, end_angle, (0, 0, 255), -1)

        sceneutil.draw_image_on(image, chart_image, position,
                                position_is_topleft=False,
                                position_is_bottom_left=True)
        cv2.putText(image, text,
                    (position[0], position[1] + text_thickness + text_size[1]),
                    font, font_scale, text_color, text_thickness, line_type)

        cv2.imshow('timer as chart', image)
        cv2.waitKey(1)
        time.sleep(1)


def draw_timer_as_time():
    text = "Hello Timer"
    current_time = 0
    duration = 20
    font = cv2.FONT_HERSHEY_SIMPLEX
    line_type = cv2.LINE_AA
    font_scale = 0.5
    text_thickness = 1
    height, width = image.shape[0:2]
    position = (int(width / 2), int(height / 2))
    text_color = BLACK

    cv2.imshow('timer as time', image)
    cv2.waitKey(1)

    remaining_time = duration - current_time
    minutes = remaining_time // 60
    seconds = remaining_time % 60
    remaining_time_text = str(minutes).zfill(2) + ":" + str(seconds).zfill(2)
    text_size, _ = cv2.getTextSize(remaining_time_text, font, font_scale, text_thickness)

    for i in range(duration + 1):
        current_time = i
        remaining_time = duration - current_time
        minutes = remaining_time // 60
        seconds = remaining_time % 60
        remaining_time_text = str(minutes).zfill(2) + ":" + str(seconds).zfill(2)

        width = text_size[0] + 2 * text_thickness
        height = text_size[1] + 4 * text_thickness
        time_image = np.zeros((height, width, 3), np.uint8)
        time_image[:] = (128, 128, 128)

        cv2.putText(time_image, remaining_time_text,
                    (text_thickness, text_thickness + text_size[1]),
                    font, font_scale, text_color, text_thickness, line_type)

        sceneutil.draw_image_on(image, time_image, position, position_is_topleft=False, position_is_bottom_left=True)
        cv2.putText(image, text,
                    (position[0], position[1] + text_thickness + text_size[1]),
                    font, font_scale, text_color, text_thickness, line_type)

        cv2.imshow('timer as time', image)
        cv2.waitKey(1)
        time.sleep(1)


def draw_timer_as_fraction():
    text = "Hello Timer"
    current_time = 0
    duration = 20
    font = cv2.FONT_HERSHEY_SIMPLEX
    line_type = cv2.LINE_AA
    font_scale = 0.5
    text_thickness = 1
    height, width = image.shape[0:2]
    position = (int(width / 2), int(height / 2))
    text_color = BLACK

    cv2.imshow('timer as fraction', image)
    cv2.waitKey(1)

    remaining_time = duration - current_time
    minutes = remaining_time // 60
    seconds = remaining_time % 60
    remaining_time_text = str(minutes).zfill(2) + ":" + str(seconds).zfill(2)
    text_size, _ = cv2.getTextSize(remaining_time_text, font, font_scale, text_thickness)

    for i in range(duration + 1):
        current_time = i
        text_size, _ = cv2.getTextSize(str(duration), font, font_scale, text_thickness)
        width = text_size[0] + 2 * text_thickness
        height = 2 * text_size[1] + 10 * text_thickness
        fraction_image = np.zeros((height, width, 3), np.uint8)
        fraction_image[:] = (128, 128, 128)

        cv2.putText(fraction_image, str(current_time).zfill(len(str(duration))),
                    (text_thickness, text_thickness + text_size[1]),
                    font, font_scale, text_color, text_thickness, line_type)
        cv2.line(fraction_image,
                 (text_thickness, 4 * text_thickness + text_size[1]),
                 (2 * text_thickness + text_size[0], 4 * text_thickness + text_size[1]),
                 text_color, text_thickness)
        cv2.putText(fraction_image, str(duration),
                    (text_thickness, 6 * text_thickness + 2 * text_size[1]),
                    font, font_scale, text_color, text_thickness, line_type)

        sceneutil.draw_image_on(image, fraction_image, position,
                                position_is_topleft=False,
                                position_is_bottom_left=True)
        cv2.putText(image, text,
                    (position[0], position[1] + text_thickness + text_size[1]),
                    font, font_scale, text_color, text_thickness, line_type)

        cv2.imshow('timer as fraction', image)
        cv2.waitKey(1)
        time.sleep(1)


# Create new blank 300x150 white image
width, height = 500, 500
image = create_blank(width, height, color=WHITE)

# draw_half_circle_rounded(image)
# draw_timer_as_chart()
# draw_timer_as_time()
draw_timer_as_fraction()

cv2.imshow('half_circle_rounded.jpg', image)
cv2.waitKey()


