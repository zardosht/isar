import cv2

from isar.scene.annotationmodel import LineAnnotation


class AnnotationTool:
    def __init__(self):
        self.img = None
        self.drawing = False

    def mouse_press_event(self, event):
        pass

    def mouse_move_event(self, event):
        pass

    def mouse_release_event(self, event):
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


class LineAnnotationTool(AnnotationTool):
    def __init__(self):
        super(LineAnnotationTool, self).__init__()
        self.line_annotation = None

    def mouse_press_event(self, event):
        print("mouse_press_event")
        self.drawing = True
        self.line_annotation = LineAnnotation()

        # convert mouse coordinates to image coordinates
        # based on the scale factor between opencv image size and
        # the camera_view image size

        self.line_annotation.start = (int(event.x()), int(event.y()))

    def mouse_move_event(self, event):
        if self.drawing:
            self.line_annotation.end = (int(event.x()), int(event.y()))

    def mouse_release_event(self, event):
        # TODO: add annotation to the scene object
        self.drawing = False

    def draw(self):
        if not self.drawing:
            return

        if not self.line_annotation or not self.line_annotation.end:
            return

        # TODO: later we must convert from relative float coordinates to image int coordinates.

        self.img = cv2.line(self.img,
                            tuple(self.line_annotation.start),
                            tuple(self.line_annotation.end),
                            self.line_annotation.color,
                            self.line_annotation.thikness)

