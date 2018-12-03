import cv2
from PyQt5.QtCore import QSize

from isar.scene.annotationmodel import LineAnnotation


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


def relative_to_image_coordinates(opencv_img_shape, rel_x, rel_y):
    # based on the scale factor between opencv image size and
    # the camera_view image size
    img_x = int(rel_x * opencv_img_shape[1])
    img_y = int(rel_y * opencv_img_shape[0])
    return img_x, img_y


def draw_annotation(opencv_img, annotation):
    annotation_tool = annotation_tools[annotation.__class__.__name__]()
    annotation_tool.img = opencv_img
    annotation_tool.drawing = True
    annotation_tool.annotation = annotation
    annotation_tool.draw()


class LineAnnotationTool(AnnotationTool):
    def __init__(self):
        super(LineAnnotationTool, self).__init__()

    def mouse_press_event(self, camera_view, event):
        print("mouse_press_event")
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

        start = relative_to_image_coordinates(self.img.shape, *(self.annotation.start))
        end = relative_to_image_coordinates(self.img.shape, *(self.annotation.end))
        self.img = cv2.line(self.img,
                            start,
                            end,
                            self.annotation.color,
                            self.annotation.thikness)


annotation_tools = {
    LineAnnotation.__name__: LineAnnotationTool

}
