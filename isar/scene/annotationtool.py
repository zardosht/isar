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
        self._drawing = False
        self.annotation = None
        self.annotations_model = None

    def set_image(self, img):
        self._img = img
        self._image_frame = Frame(self._img.shape[1], self._img.shape[0])

    def set_drawing(self, drawing):
        self._drawing = drawing

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
    annotation_tool.annotation = annotation
    annotation_tool.set_drawing(True)
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
        self.set_drawing(True)
        self.annotation = CircleAnnotation()

        # convert mouse coordinates to image coordinates
        camera_view_size = Frame(camera_view.size().width(), camera_view.size().height())
        img_x, img_y = util.mouse_coordinates_to_image_coordinates(
            event.pos().x(), event.pos().y(), camera_view_size, self._image_frame)
        self.annotation.center.set_value((img_x, img_y))

    def mouse_move_event(self, camera_view, event):
        if self._drawing:
            camera_view_size = Frame(camera_view.size().width(), camera_view.size().height())
            img_x, img_y = util.mouse_coordinates_to_image_coordinates(
                event.pos().x(), event.pos().y(), camera_view_size, self._image_frame)
            radius = util.calc_distance(self.annotation.center.get_value(), (img_x, img_y))
            self.annotation.radius.set_value(int(radius))

    def mouse_release_event(self, camera_view, event):
        if self.is_annotation_valid():
            self.annotations_model.add_annotation(self.annotation)
        self.set_drawing(False)

    def is_annotation_valid(self):
        # Has the circle the minimum radius?
        radius = self.annotation.radius.get_value()
        if radius is None:
            return False
        if radius < CircleAnnotation.MINIMUM_RADIUS:
            return False

        return True

    def draw(self):
        if not self._drawing:
            return

        if not self.annotation or not self.annotation.radius.get_value():
            return

        center = util.get_point_in_ref_frame(self.annotation.center.get_value(), self.reference_frame)
        radius = self.annotation.radius.get_value()

        cv2.circle(self._img,
                   center,
                   radius,
                   self.annotation.color.get_value(),
                   self.annotation.thikness.get_value())


class RectangleAnnotationTool(AnnotationTool):
    def __init__(self):
        super(RectangleAnnotationTool, self).__init__()
        self.v1 = None
        self.v2 = None
        self.color = (255, 0, 255)
        self.thikness = 3

    def mouse_press_event(self, camera_view, event):
        self.v1 = None
        self.v2 = None
        self.set_drawing(True)

        # convert mouse coordinates to image coordinates
        camera_view_size = Frame(camera_view.size().width(), camera_view.size().height())
        img_x, img_y = util.mouse_coordinates_to_image_coordinates(
            event.pos().x(), event.pos().y(), camera_view_size, self._image_frame)
        self.v1 = (img_x, img_y)

    def mouse_move_event(self, camera_view, event):
        if self._drawing:
            camera_view_size = Frame(camera_view.size().width(), camera_view.size().height())
            img_x, img_y = util.mouse_coordinates_to_image_coordinates(
                event.pos().x(), event.pos().y(), camera_view_size, self._image_frame)
            self.v2 = (img_x, img_y)

    def mouse_release_event(self, camera_view, event):
        if self.v2 is None or self.v1 is None:
            self.set_drawing(False)
            return

        width = self.v2[0] - self.v1[0]
        right_to_left = False
        if width < 0:
            right_to_left = True

        bottom_up = False
        height = self.v2[1] - self.v1[1]
        if height < 0:
            bottom_up = True

        position = [self.v1[0], self.v1[1]]
        if right_to_left:
            position[0] = self.v2[0]

        if bottom_up:
            position[1] = self.v2[1]

        if self.is_annotation_valid(width, height):
            annotation = RectangleAnnotation()
            annotation.set_position(position)
            annotation.width.set_value(abs(width))
            annotation.height.set_value(abs(height))
            self.annotations_model.add_annotation(annotation)

        self.set_drawing(False)

    def set_drawing(self, drawing):
        self._drawing = drawing

    @staticmethod
    def is_annotation_valid(width, height):
        return abs(width) >= RectangleAnnotation.MINIMUM_WIDTH \
               and abs(height) >= RectangleAnnotation.MINIMUM_HEIGHT

    def draw(self):
        if not self._drawing:
            return

        color = self.color
        thikness = self.thikness
        if self.annotation:
            self.v1 = util.get_point_in_ref_frame(self.annotation.position.get_value(), self.reference_frame)
            width = self.annotation.width.get_value()
            height = self.annotation.height.get_value()
            self.v2 = (self.v1[0] + width, self.v1[1] + height)
            color = self.annotation.color.get_value()
            thikness = self.annotation.thikness.get_value()

        if self.v2 is None:
            return

        cv2.rectangle(self._img,
                      tuple(self.v1),
                      tuple(self.v2),
                      color,
                      thikness)


class LineAnnotationTool(AnnotationTool):
    def __init__(self):
        super(LineAnnotationTool, self).__init__()

    def mouse_press_event(self, camera_view, event):
        self.set_drawing(True)
        self.annotation = LineAnnotation()

        # convert mouse coordinates to image coordinates
        camera_view_size = Frame(camera_view.size().width(), camera_view.size().height())
        img_x, img_y = util.mouse_coordinates_to_image_coordinates(
            event.pos().x(), event.pos().y(), camera_view_size, self._image_frame)
        self.annotation.start.set_value((img_x, img_y))

    def mouse_move_event(self, camera_view, event):
        if self._drawing:
            camera_view_size = Frame(camera_view.size().width(), camera_view.size().height())
            img_x, img_y = util.mouse_coordinates_to_image_coordinates(
                event.pos().x(), event.pos().y(), camera_view_size, self._image_frame)
            self.annotation.end.set_value((img_x, img_y))

    def mouse_release_event(self, camera_view, event):
        if self.is_annotation_valid():
            self.annotations_model.add_annotation(self.annotation)
        self.set_drawing(False)

    def draw(self):
        if not self._drawing:
            return

        if not self.annotation or not self.annotation.end.get_value():
            return

        start = util.get_point_in_ref_frame(self.annotation.start.get_value(), self.reference_frame)
        end = util.get_point_in_ref_frame(self.annotation.end.get_value(), self.reference_frame)

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
