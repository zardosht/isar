import logging
import math
import cv2

from isar.scene import util
from isar.scene.annotationmodel import LineAnnotation, RectangleAnnotation, CircleAnnotation, TimerAnnotation, \
    VideoAnnotation, AudioAnnotation, ImageAnnotation, TextAnnotation, ArrowAnnotation, RelationshipAnnotation, \
    SelectBoxAnnotation
from isar.scene.util import Frame

logger = logging.getLogger("isar.annotationtool")


class AnnotationTool:
    def __init__(self):
        self._img = None
        self._image_frame = None
        self.reference_frame = None
        self.drawing = False
        self.annotation = None
        self.annotations_model = None

    def set_image(self, img):
        self._img = img
        self._image_frame = Frame(self._img.shape[1], self._img.shape[0])

    def mouse_press_event(self, qwidget, event):
        pass

    def mouse_move_event(self, qwidget, event):
        pass

    def mouse_release_event(self, qwidget, event):
        pass

    def draw(self):
        pass


def draw_annotation(opencv_img, annotation, reference_frame=None):
    annotation_tool = annotation_tools[annotation.__class__.__name__]
    annotation_tool.set_image(opencv_img)
    annotation_tool.reference_frame = reference_frame
    annotation_tool.drawing = True
    annotation_tool.annotation = annotation
    annotation_tool.draw()


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

        # convert mouse coordinates to image coordinates
        camera_view_size = Frame(camera_view.size().width(), camera_view.size().height())
        img_x, img_y = util.mouse_coordinates_to_image_coordinates(
            event.pos().x(), event.pos().y(), camera_view_size, self._image_frame)
        self.annotation.center.set_value((img_x, img_y))

    def mouse_move_event(self, camera_view, event):
        if self.drawing:
            camera_view_size = Frame(camera_view.size().width(), camera_view.size().height())
            img_x, img_y = util.mouse_coordinates_to_image_coordinates(
                event.pos().x(), event.pos().y(), camera_view_size, self._image_frame)
            radius = util.calc_distance(self.annotation.center.get_value(), (img_x, img_y))
            self.annotation.radius.set_value(int(radius))

    def mouse_release_event(self, camera_view, event):
        if self.is_annotation_valid():
            self.annotations_model.add_annotation(self.annotation)
        self.drawing = False

    def is_annotation_valid(self):
        # Has the circle the minimum radius?
        radius = self.annotation.radius.get_value()
        if radius is None:
            return False
        if radius < CircleAnnotation.MINIMUM_RADIUS:
            return False

        return True

    def draw(self):
        if not self.drawing:
            return

        if not self.annotation or not self.annotation.radius.get_value():
            return

        center = self.annotation.center.get_value()
        radius = self.annotation.radius.get_value()

        cv2.circle(self._img,
                   center,
                   radius,
                   self.annotation.color.get_value(),
                   self.annotation.thikness.get_value())


class RectangleAnnotationTool(AnnotationTool):
    def __init__(self):
        super(RectangleAnnotationTool, self).__init__()

    def mouse_press_event(self, camera_view, event):
        self.drawing = True
        self.annotation = RectangleAnnotation()

        # convert mouse coordinates to image coordinates
        camera_view_size = Frame(camera_view.size().width(), camera_view.size().height())
        img_x, img_y = util.mouse_coordinates_to_image_coordinates(
            event.pos().x(), event.pos().y(), camera_view_size, self._image_frame)
        self.annotation.vertex1.set_value((img_x, img_y))

    def mouse_move_event(self, camera_view, event):
        if self.drawing:
            camera_view_size = Frame(camera_view.size().width(), camera_view.size().height())
            img_x, img_y = util.mouse_coordinates_to_image_coordinates(
                event.pos().x(), event.pos().y(), camera_view_size, self._image_frame)
            self.annotation.vertex2.set_value((img_x, img_y))

    def mouse_release_event(self, camera_view, event):
        if self.is_annotation_valid():
            self.annotations_model.add_annotation(self.annotation)

        self.drawing = False

    def is_annotation_valid(self):
        # Has the rectangle the minimum area?
        area = util.calc_rect_area(self.annotation.vertex1.get_value(), self.annotation.vertex2.get_value())
        if area is None:
            return False
        if area < RectangleAnnotation.MINIMUM_AREA:
            return False

        return True

    def draw(self):
        if not self.drawing:
            return

        if not self.annotation or not self.annotation.vertex2.get_value():
            return

        vertex1 = self.annotation.vertex1.get_value()
        vertex2 = self.annotation.vertex2.get_value()

        cv2.rectangle(self._img,
                      vertex1,
                      vertex2,
                      self.annotation.color.get_value(),
                      self.annotation.thikness.get_value())


class LineAnnotationTool(AnnotationTool):
    def __init__(self):
        super(LineAnnotationTool, self).__init__()

    def mouse_press_event(self, camera_view, event):
        self.drawing = True
        self.annotation = LineAnnotation()

        # convert mouse coordinates to image coordinates
        camera_view_size = Frame(camera_view.size().width(), camera_view.size().height())
        img_x, img_y = util.mouse_coordinates_to_image_coordinates(
            event.pos().x(), event.pos().y(), camera_view_size, self._image_frame)
        self.annotation.start.set_value((img_x, img_y))

    def mouse_move_event(self, camera_view, event):
        if self.drawing:
            camera_view_size = Frame(camera_view.size().width(), camera_view.size().height())
            img_x, img_y = util.mouse_coordinates_to_image_coordinates(
                event.pos().x(), event.pos().y(), camera_view_size, self._image_frame)
            self.annotation.end.set_value((img_x, img_y))

    def mouse_release_event(self, camera_view, event):
        if self.is_annotation_valid():
            self.annotations_model.add_annotation(self.annotation)
        self.drawing = False

    def draw(self):
        if not self.drawing:
            return

        if not self.annotation or not self.annotation.end.get_value():
            return

        start = self.annotation.start.get_value()
        end = self.annotation.end.get_value()

        cv2.line(self._img,
                 start,
                 end,
                 self.annotation.color.get_value(),
                 self.annotation.thikness.get_value())

    def is_annotation_valid(self):
        # Has the lind the minimum lenght?
        length = util.calc_distance(self.annotation.start.get_value(), self.annotation.end.get_value())
        if length is None:
            return False
        if length < LineAnnotation.MINIMUM_LENGTH:
            return False

        return True


class SelectAnnotationTool(AnnotationTool):
    def __init__(self):
        super(SelectAnnotationTool, self).__init__()

    def mouse_press_event(self, camera_view, event):
        logger.info("Not implemented.")
        pass

    def mouse_move_event(self, camera_view, event):
        logger.info("Not implemented.")
        pass

    def mouse_release_event(self, camera_view, event):
        logger.info("Not implemented.")
        pass

    def draw(self):
        pass


class TimerAnnotationTool(AnnotationTool):
    def __init__(self):
        super(TimerAnnotationTool, self).__init__()

    def mouse_press_event(self, camera_view, event):
        logger.info("Not implemented.")
        pass

    def mouse_move_event(self, camera_view, event):
        logger.info("Not implemented.")
        pass

    def mouse_release_event(self, camera_view, event):
        logger.info("Not implemented.")
        pass

    def draw(self):
        logger.info("Not implemented.")
        pass


class VideoAnnotationTool(AnnotationTool):
    def __init__(self):
        super(VideoAnnotationTool, self).__init__()

    def mouse_press_event(self, camera_view, event):
        logger.info("Not implemented.")
        pass

    def mouse_move_event(self, camera_view, event):
        logger.info("Not implemented.")
        pass

    def mouse_release_event(self, camera_view, event):
        logger.info("Not implemented.")
        pass

    def draw(self):
        logger.info("Not implemented.")
        pass


class AudioAnnotationTool(AnnotationTool):
    def __init__(self):
        super(AudioAnnotationTool, self).__init__()

    def mouse_press_event(self, camera_view, event):
        logger.info("Not implemented.")
        pass

    def mouse_move_event(self, camera_view, event):
        logger.info("Not implemented.")
        pass

    def mouse_release_event(self, camera_view, event):
        logger.info("Not implemented.")
        pass

    def draw(self):
        logger.info("Not implemented.")
        pass


class ImageAnnotationTool(AnnotationTool):
    def __init__(self):
        super(ImageAnnotationTool, self).__init__()

    def mouse_press_event(self, camera_view, event):
        logger.info("Not implemented.")
        pass

    def mouse_move_event(self, camera_view, event):
        logger.info("Not implemented.")
        pass

    def mouse_release_event(self, camera_view, event):
        logger.info("Not implemented.")
        pass

    def draw(self):
        logger.info("Not implemented.")
        pass


class TextAnnotationTool(AnnotationTool):
    def __init__(self):
        super(TextAnnotationTool, self).__init__()

    def mouse_press_event(self, camera_view, event):
        logger.info("Not implemented.")
        pass

    def mouse_move_event(self, camera_view, event):
        logger.info("Not implemented.")
        pass

    def mouse_release_event(self, camera_view, event):
        logger.info("Not implemented.")
        pass

    def draw(self):
        logger.info("Not implemented.")
        pass


class RelationshipAnnotationTool(AnnotationTool):
    def __init__(self):
        super(RelationshipAnnotationTool, self).__init__()

    def mouse_press_event(self, camera_view, event):
        logger.info("Not implemented.")
        pass

    def mouse_move_event(self, camera_view, event):
        logger.info("Not implemented.")
        pass

    def mouse_release_event(self, camera_view, event):
        logger.info("Not implemented.")
        pass

    def draw(self):
        logger.info("Not implemented.")
        pass


class ArrowAnnotationTool(AnnotationTool):
    def __init__(self):
        super(ArrowAnnotationTool, self).__init__()

    def mouse_press_event(self, camera_view, event):
        logger.info("Not implemented.")
        pass

    def mouse_move_event(self, camera_view, event):
        logger.info("Not implemented.")
        pass

    def mouse_release_event(self, camera_view, event):
        logger.info("Not implemented.")
        pass

    def draw(self):
        logger.info("Not implemented.")
        pass


class SelectBoxAnnotationTool(AnnotationTool):
    def __init__(self):
        super(SelectBoxAnnotationTool, self).__init__()

    def mouse_press_event(self, camera_view, event):
        logger.info("Not implemented.")
        pass

    def mouse_move_event(self, camera_view, event):
        logger.info("Not implemented.")
        pass

    def mouse_release_event(self, camera_view, event):
        logger.info("Not implemented.")
        pass

    def draw(self):
        logger.info("Not implemented.")
        pass


annotation_tools = {
    LineAnnotation.__name__: LineAnnotationTool(),
    RectangleAnnotation.__name__: RectangleAnnotationTool(),
    CircleAnnotation.__name__: CircleAnnotationTool(),
    TimerAnnotation.__name__: TimerAnnotationTool(),
    VideoAnnotation.__name__: VideoAnnotationTool(),
    AudioAnnotation.__name__: AudioAnnotationTool(),
    ImageAnnotation.__name__: ImageAnnotationTool(),
    TextAnnotation.__name__: TextAnnotationTool(),
    ArrowAnnotation.__name__: ArrowAnnotationTool(),
    RelationshipAnnotation.__name__: RelationshipAnnotationTool(),
    SelectBoxAnnotation.__name__: SelectBoxAnnotationTool()
}

annotation_tool_btns = {
    "line_btn": LineAnnotationTool(),
    "rectangle_btn": RectangleAnnotationTool(),
    "circle_btn": CircleAnnotationTool(),
    "select_btn": SelectAnnotationTool(),
    "select_box_btn": SelectBoxAnnotationTool(),
    "text_btn": TextAnnotationTool(),
    "timer_btn": TimerAnnotationTool(),
    "video_btn": VideoAnnotationTool(),
    "audio_btn": AudioAnnotationTool(),
    "relationship_btn": RelationshipAnnotationTool(),
    "arrow_btn": ArrowAnnotationTool(),
    "image_btn": ImageAnnotationTool()
}

