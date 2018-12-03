import math

import cv2
from PyQt5.QtCore import QSize

from isar.scene.annotationmodel import LineAnnotation, RectangleAnnotation, CircleAnnotation


class AnnotationTool:
    def __init__(self):
        self.img = None
        self.drawing = False
        self.annotation = None
        self.scene = None

    def mouse_press_event(self, qwidget, event):
        pass

    def mouse_move_event(self, qwidget, event):
        pass

    def mouse_release_event(self, qwidget, event):
        pass

    def draw(self):
        pass


def relative_to_image_coordinates(opencv_img_shape, rel_x, rel_y):
    # based on the scale factor between opencv image size and
    # the camera_view image size
    img_x = int(rel_x * opencv_img_shape[1])
    img_y = int(rel_y * opencv_img_shape[0])
    return img_x, img_y


def distance_to_image_coordinates(opencv_img_shape, rel_distance):
    # based on the scale factor between opencv image size and
    # the camera_view image size
    # opencv_img_shape[1] is width
    img_dist = int(rel_distance * opencv_img_shape[1])
    return int(img_dist)


def draw_annotation(opencv_img, annotation):
    annotation_tool = annotation_tools[annotation.__class__.__name__]()
    annotation_tool.img = opencv_img
    annotation_tool.drawing = True
    annotation_tool.annotation = annotation
    annotation_tool.draw()


def calc_distance(p1, p2):
    return math.sqrt(math.pow(p1[0] - p2[0], 2) + math.pow(p1[1] - p2[1], 2))


"""
Text
Arrow
SelectButton
Line
Circle
Rectangle
Relationship
Image
Video
Audio
Timer
"""


class CircleAnnotationTool(AnnotationTool):
    def __init__(self):
        super(CircleAnnotationTool, self).__init__()

    def mouse_press_event(self, camera_view, event):
        self.drawing = True
        self.annotation = CircleAnnotation()

        # convert mouse coordinates to relative image coordinates
        rel_x = event.x() / camera_view.size().width()
        rel_y = event.y() / camera_view.size().height()
        self.annotation.center = (rel_x, rel_y)

    def mouse_move_event(self, camera_view, event):
        if self.drawing:
            rel_x = event.x() / camera_view.size().width()
            rel_y = event.y() / camera_view.size().height()
            self.annotation.radius = calc_distance(self.annotation.center, (rel_x, rel_y))

    def mouse_release_event(self, camera_view, event):
        self.scene.annotations.append(self.annotation)
        self.drawing = False

    def draw(self):
        if not self.drawing:
            return

        if not self.annotation or not self.annotation.radius:
            return

        center = relative_to_image_coordinates(self.img.shape, *self.annotation.center)
        radius = distance_to_image_coordinates(self.img.shape, self.annotation.radius)

        cv2.circle(self.img,
                   center,
                   radius,
                   self.annotation.color,
                   self.annotation.thikness)


class RectangleAnnotationTool(AnnotationTool):
    def __init__(self):
        super(RectangleAnnotationTool, self).__init__()

    def mouse_press_event(self, camera_view, event):
        self.drawing = True
        self.annotation = RectangleAnnotation()

        # convert mouse coordinates to relative image coordinates
        rel_x = event.x() / camera_view.size().width()
        rel_y = event.y() / camera_view.size().height()
        self.annotation.vertex1 = (rel_x, rel_y)

    def mouse_move_event(self, camera_view, event):
        if self.drawing:
            rel_x = event.x() / camera_view.size().width()
            rel_y = event.y() / camera_view.size().height()
            self.annotation.vertex2 = (rel_x, rel_y)

    def mouse_release_event(self, camera_view, event):
        self.scene.annotations.append(self.annotation)
        self.drawing = False

    def draw(self):
        if not self.drawing:
            return

        if not self.annotation or not self.annotation.vertex2:
            return

        vertex1 = relative_to_image_coordinates(self.img.shape, *self.annotation.vertex1)
        vertex2 = relative_to_image_coordinates(self.img.shape, *self.annotation.vertex2)

        cv2.rectangle(self.img,
                      vertex1,
                      vertex2,
                      self.annotation.color,
                      self.annotation.thikness)


class LineAnnotationTool(AnnotationTool):
    def __init__(self):
        super(LineAnnotationTool, self).__init__()

    def mouse_press_event(self, camera_view, event):
        self.drawing = True
        self.annotation = LineAnnotation()

        # convert mouse coordinates to relative image coordinates
        rel_x = event.x() / camera_view.size().width()
        rel_y = event.y() / camera_view.size().height()
        self.annotation.start = (rel_x, rel_y)

    def mouse_move_event(self, camera_view, event):
        if self.drawing:
            rel_x = event.x() / camera_view.size().width()
            rel_y = event.y() / camera_view.size().height()
            self.annotation.end = (rel_x, rel_y)

    def mouse_release_event(self, camera_view, event):
        self.scene.annotations.append(self.annotation)
        self.drawing = False

    def draw(self):
        if not self.drawing:
            return

        if not self.annotation or not self.annotation.end:
            return

        start = relative_to_image_coordinates(self.img.shape, *self.annotation.start)
        end = relative_to_image_coordinates(self.img.shape, *self.annotation.end)
        self.img = cv2.line(self.img,
                            start,
                            end,
                            self.annotation.color,
                            self.annotation.thikness)


class SelectAnnotationTool(AnnotationTool):
    def __init__(self):
        super(SelectAnnotationTool, self).__init__()

    def mouse_press_event(self, camera_view, event):
        pass

    def mouse_move_event(self, camera_view, event):
        pass

    def mouse_release_event(self, camera_view, event):
       pass

    def draw(self):
       pass


annotation_tools = {
    LineAnnotation.__name__: LineAnnotationTool,
    RectangleAnnotation.__name__: RectangleAnnotationTool,
    CircleAnnotation.__name__: CircleAnnotationTool,
    SelectAnnotationTool.__name__: SelectAnnotationTool

}
