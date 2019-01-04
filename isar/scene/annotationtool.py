import logging
import math
import cv2

from isar.scene import util
from isar.scene.annotationmodel import LineAnnotation, RectangleAnnotation, CircleAnnotation, TimerAnnotation, \
    VideoAnnotation, AudioAnnotation, ImageAnnotation, TextAnnotation, ArrowAnnotation, RelationshipAnnotation, \
    SelectBoxAnnotation
from isar.scene.util import ImageFrame

logger = logging.getLogger("isar.annotationtool")


class AnnotationTool:
    def __init__(self):
        self.img = None
        self.reference_frame = None
        self.drawing = False
        self.annotation = None
        self.annotations_model = None

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
    annotation_tool.img = opencv_img
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

        # convert mouse coordinates to relative image coordinates
        camera_view_size = ImageFrame(camera_view.size().width(), camera_view.size().height())
        rel_x, rel_y = util.image_coordinates_to_relative_coordinates(
            camera_view_size, event.pos().x(), event.pos().y())
        self.annotation.center.set_value((rel_x, rel_y))

    def mouse_move_event(self, camera_view, event):
        if self.drawing:
            camera_view_size = ImageFrame(camera_view.size().width(), camera_view.size().height())
            rel_x, rel_y = util.image_coordinates_to_relative_coordinates(
                camera_view_size, event.pos().x(), event.pos().y())
            radius = util.calc_distance(self.annotation.center.get_value(), (rel_x, rel_y))
            self.annotation.radius.set_value(radius)

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

        image_frame = ImageFrame(self.img.shape[1], self.img.shape[0])
        center = util.relative_coordinates_to_image_coordinates(
            image_frame, *self.annotation.center.get_value(), self.reference_frame)
        radius = util.relative_distance_to_image_coordinates(image_frame, self.annotation.radius.get_value())

        cv2.circle(self.img,
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

        # convert mouse coordinates to relative image coordinates
        camera_view_size = ImageFrame(camera_view.size().width(), camera_view.size().height())
        rel_x, rel_y = util.image_coordinates_to_relative_coordinates(
            camera_view_size, event.pos().x(), event.pos().y())
        self.annotation.vertex1.set_value((rel_x, rel_y))

    def mouse_move_event(self, camera_view, event):
        if self.drawing:
            camera_view_size = ImageFrame(camera_view.size().width(), camera_view.size().height())
            rel_x, rel_y = util.image_coordinates_to_relative_coordinates(
                camera_view_size, event.pos().x(), event.pos().y())
            self.annotation.vertex2.set_value((rel_x, rel_y))

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

        image_frame = ImageFrame(self.img.shape[1], self.img.shape[0])
        vertex1 = util.relative_coordinates_to_image_coordinates(
            image_frame, *self.annotation.vertex1.get_value(), self.reference_frame)
        vertex2 = util.relative_coordinates_to_image_coordinates(
            image_frame, *self.annotation.vertex2.get_value(), self.reference_frame)

        cv2.rectangle(self.img,
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

        # convert mouse coordinates to relative image coordinates
        camera_view_size = ImageFrame(camera_view.size().width(), camera_view.size().height())
        rel_x, rel_y = util.image_coordinates_to_relative_coordinates(
            camera_view_size, event.pos().x(), event.pos().y())
        self.annotation.start.set_value((rel_x, rel_y))

    def mouse_move_event(self, camera_view, event):
        if self.drawing:
            camera_view_size = ImageFrame(camera_view.size().width(), camera_view.size().height())
            rel_x, rel_y = util.image_coordinates_to_relative_coordinates(
                camera_view_size, event.pos().x(), event.pos().y())
            self.annotation.end.set_value((rel_x, rel_y))

    def mouse_release_event(self, camera_view, event):
        if self.is_annotation_valid():
            self.annotations_model.add_annotation(self.annotation)
        self.drawing = False

    def draw(self):
        if not self.drawing:
            return

        if not self.annotation or not self.annotation.end.get_value():
            return

        image_frame = ImageFrame(self.img.shape[1], self.img.shape[0])
        start = util.relative_coordinates_to_image_coordinates(
            image_frame, *self.annotation.start.get_value(), self.reference_frame)
        end = util.relative_coordinates_to_image_coordinates(
            image_frame, *self.annotation.end.get_value(), self.reference_frame)
        self.img = cv2.line(self.img,
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

