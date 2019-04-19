import logging
import math
import os

import cv2
from PyQt5.QtWidgets import QMessageBox, QFileDialog

from isar.scene import sceneutil, scenemodel
from isar.scene.annotationmodel import LineAnnotation, RectangleAnnotation, CircleAnnotation, TimerAnnotation, \
    VideoAnnotation, AudioAnnotation, ImageAnnotation, TextAnnotation, ArrowAnnotation, RelationshipAnnotation, \
    SelectBoxAnnotation
from isar.scene.sceneutil import Frame

logger = logging.getLogger("isar.scene.annotationtool")


class AnnotationTool:
    def __init__(self):
        self._img = None
        self._image_frame = None
        self.phys_obj = None
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


def draw_annotation(opencv_img, annotation, phys_obj=None):
    annotation_tool = annotation_tools[annotation.__class__.__name__]
    annotation_tool.set_image(opencv_img)
    annotation_tool.phys_obj = phys_obj
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
        img_x, img_y = sceneutil.mouse_coordinates_to_image_coordinates(
            event.pos().x(), event.pos().y(), camera_view_size, self._image_frame)
        self.annotation.center.set_value((img_x, img_y))

    def mouse_move_event(self, camera_view, event):
        if self._drawing:
            camera_view_size = Frame(camera_view.size().width(), camera_view.size().height())
            img_x, img_y = sceneutil.mouse_coordinates_to_image_coordinates(
                event.pos().x(), event.pos().y(), camera_view_size, self._image_frame)
            radius = sceneutil.calc_distance(self.annotation.center.get_value(), (img_x, img_y))
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

        center = sceneutil.convert_object_to_image(self.annotation.center.get_value(), self.phys_obj)
        radius = self.annotation.radius.get_value()

        cv2.circle(self._img,
                   center,
                   radius,
                   self.annotation.color.get_value(),
                   self.annotation.thickness.get_value())


class RectangleAnnotationTool(AnnotationTool):
    def __init__(self):
        super(RectangleAnnotationTool, self).__init__()
        self.v1 = None
        self.v2 = None
        self.color = (255, 0, 255)
        self.thickness = 3

    def mouse_press_event(self, camera_view, event):
        self.v1 = None
        self.v2 = None
        self.set_drawing(True)

        # convert mouse coordinates to image coordinates
        camera_view_size = Frame(camera_view.size().width(), camera_view.size().height())
        img_x, img_y = sceneutil.mouse_coordinates_to_image_coordinates(
            event.pos().x(), event.pos().y(), camera_view_size, self._image_frame)
        self.v1 = (img_x, img_y)

    def mouse_move_event(self, camera_view, event):
        if self._drawing:
            camera_view_size = Frame(camera_view.size().width(), camera_view.size().height())
            img_x, img_y = sceneutil.mouse_coordinates_to_image_coordinates(
                event.pos().x(), event.pos().y(), camera_view_size, self._image_frame)
            self.v2 = (img_x, img_y)

    def mouse_release_event(self, camera_view, event):
        if self.v2 is None or self.v1 is None:
            self.set_drawing(False)
            return

        width = self.v2[0] - self.v1[0]
        height = self.v2[1] - self.v1[1]
        position = [self.v1[0] + int(width / 2), self.v1[1] + int(height / 2)]

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
        thickness = self.thickness
        if self.annotation:
            # position = util.convert_object_to_image(self.annotation.position.get_value(), self.phys_obj)
            position = self.annotation.position.get_value()
            width = self.annotation.width.get_value()
            height = self.annotation.height.get_value()
            v1 = [0, 0]
            v1[0] = position[0] - int(width / 2)
            v1[1] = position[1] - int(height / 2)
            self.v1 = sceneutil.convert_object_to_image(v1, self.phys_obj)
            v2 = [0, 0]
            v2[0] = position[0] + int(width / 2)
            v2[1] = position[1] + int(height / 2)
            self.v2 = sceneutil.convert_object_to_image(v2, self.phys_obj)
            color = self.annotation.color.get_value()
            thickness = self.annotation.thickness.get_value()

        if self.v2 is None:
            return

        cv2.rectangle(self._img,
                      tuple(self.v1),
                      tuple(self.v2),
                      color,
                      thickness)


class LineAnnotationTool(AnnotationTool):
    def __init__(self):
        super(LineAnnotationTool, self).__init__()

    def mouse_press_event(self, camera_view, event):
        self.set_drawing(True)
        self.annotation = LineAnnotation()

        # convert mouse coordinates to image coordinates
        camera_view_size = Frame(camera_view.size().width(), camera_view.size().height())
        img_x, img_y = sceneutil.mouse_coordinates_to_image_coordinates(
            event.pos().x(), event.pos().y(), camera_view_size, self._image_frame)
        self.annotation.start.set_value((img_x, img_y))

    def mouse_move_event(self, camera_view, event):
        if self._drawing:
            camera_view_size = Frame(camera_view.size().width(), camera_view.size().height())
            img_x, img_y = sceneutil.mouse_coordinates_to_image_coordinates(
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

        start = sceneutil.convert_object_to_image(self.annotation.start.get_value(), self.phys_obj)
        end = sceneutil.convert_object_to_image(self.annotation.end.get_value(), self.phys_obj)

        cv2.line(self._img,
                 start,
                 end,
                 self.annotation.color.get_value(),
                 self.annotation.thickness.get_value())

    def is_annotation_valid(self):
        # Has the lind the minimum lenght?
        length = sceneutil.calc_distance(self.annotation.start.get_value(), self.annotation.end.get_value())
        if length is None:
            return False
        if length < LineAnnotation.MINIMUM_LENGTH:
            return False

        return True


class TextAnnotationTool(AnnotationTool):
    def __init__(self):
        super().__init__()

    def mouse_press_event(self, camera_view, event):
        self.set_drawing(True)
        self.annotation = TextAnnotation()

        # convert mouse coordinates to image coordinates
        camera_view_size = Frame(camera_view.size().width(), camera_view.size().height())
        img_x, img_y = sceneutil.mouse_coordinates_to_image_coordinates(
            event.pos().x(), event.pos().y(), camera_view_size, self._image_frame)
        self.annotation.position.set_value((img_x, img_y))

    def mouse_move_event(self, camera_view, event):
        # logger.info("Not implemented.")
        pass

    def mouse_release_event(self, camera_view, event):
        if self.is_annotation_valid():
            self.annotations_model.add_annotation(self.annotation)
        self.set_drawing(False)

    def draw(self):
        if not self._drawing:
            return

        if not self.annotation or not self.annotation.text.get_value():
            return

        position = sceneutil.convert_object_to_image(self.annotation.position.get_value(), self.phys_obj)
        text = self.annotation.text.get_value()
        font_scale = self.annotation.font_scale.get_value()
        color = self.annotation.color.get_value()
        thickness = self.annotation.thickness.get_value()

        # TODO: add font property to TextAnnotation()
        font = cv2.FONT_HERSHEY_SIMPLEX
        line_type = cv2.LINE_AA

        text_size, _ = cv2.getTextSize(text, font, font_scale, thickness)
        x, y0 = position
        for i, line in enumerate(text.split("\n")):
            y = y0 + i * (text_size[1] + 10)
            cv2.putText(self._img,
                        line,
                        (x, y),
                        font,
                        font_scale,
                        color,
                        thickness,
                        line_type)

    def is_annotation_valid(self):
        text = self.annotation.text.get_value()
        if text is None or text.isspace():
            return False
        else:
            return True


class ArrowAnnotationTool(AnnotationTool):
    def __init__(self):
        super(ArrowAnnotationTool, self).__init__()

    def mouse_press_event(self, camera_view, event):
        self.set_drawing(True)
        self.annotation = ArrowAnnotation()

        # convert mouse coordinates to image coordinates
        camera_view_size = Frame(camera_view.size().width(), camera_view.size().height())
        img_x, img_y = sceneutil.mouse_coordinates_to_image_coordinates(
            event.pos().x(), event.pos().y(), camera_view_size, self._image_frame)
        self.annotation.head.set_value((img_x, img_y))

    def mouse_move_event(self, camera_view, event):
        if self._drawing:
            camera_view_size = Frame(camera_view.size().width(), camera_view.size().height())
            img_x, img_y = sceneutil.mouse_coordinates_to_image_coordinates(
                event.pos().x(), event.pos().y(), camera_view_size, self._image_frame)
            self.annotation.tail.set_value((img_x, img_y))

    def mouse_release_event(self, camera_view, event):
        if self.is_annotation_valid():
            self.annotations_model.add_annotation(self.annotation)
        self.set_drawing(False)

    def draw(self):
        if not self._drawing:
            return

        if not self.annotation or not self.annotation.tail.get_value():
            return

        head = sceneutil.convert_object_to_image(self.annotation.head.get_value(), self.phys_obj)
        tail = sceneutil.convert_object_to_image(self.annotation.tail.get_value(), self.phys_obj)

        text = self.annotation.text.get_value()
        text = " " + text + " "
        font_scale = self.annotation.font_scale.get_value()
        text_color = self.annotation.text_color.get_value()
        text_thickness = self.annotation.text_thickness.get_value()

        # TODO: add font property to TextAnnotation()
        font = cv2.FONT_HERSHEY_SIMPLEX
        line_type = cv2.LINE_AA
        tip_length = self.annotation.tip_length.get_value()

        text_size, _ = cv2.getTextSize(text, font, font_scale, text_thickness)
        left2right, _ = sceneutil.get_left2right_topdown(tail, head)

        text_position = list(tail)
        if left2right:
            text_position[0] = tail[0] - text_size[0]

        cv2.putText(self._img,
                    text,
                    tuple(text_position),
                    font,
                    font_scale,
                    text_color,
                    text_thickness,
                    line_type)

        cv2.arrowedLine(self._img,
                        tuple(tail),
                        tuple(head),
                        self.annotation.color.get_value(),
                        self.annotation.thickness.get_value(),
                        line_type,
                        tipLength=tip_length
                )

    def is_annotation_valid(self):
        # Has the lind the minimum lenght?
        length = sceneutil.calc_distance(self.annotation.tail.get_value(), self.annotation.head.get_value())
        if length is None:
            return False
        if length < ArrowAnnotation.MINIMUM_LENGTH:
            return False

        return True


class ImageAnnotationTool(AnnotationTool):
    image_cache = {}

    def __init__(self):
        super(ImageAnnotationTool, self).__init__()
        self.v1 = None
        self.v2 = None
        self.color = (255, 0, 255)
        self.thickness = 3

    def mouse_press_event(self, camera_view, event):
        self.v1 = None
        self.v2 = None
        if scenemodel.current_project is None:
            QMessageBox.warning(None,
                                "Error",
                                "You first need to create a proejct to add Image, Audio, and Video annotations.")
            return

        self.set_drawing(True)

        # convert mouse coordinates to image coordinates
        camera_view_size = Frame(camera_view.size().width(), camera_view.size().height())
        img_x, img_y = sceneutil.mouse_coordinates_to_image_coordinates(
            event.pos().x(), event.pos().y(), camera_view_size, self._image_frame)
        self.v1 = (img_x, img_y)

    def mouse_move_event(self, camera_view, event):
        if self._drawing:
            camera_view_size = Frame(camera_view.size().width(), camera_view.size().height())
            img_x, img_y = sceneutil.mouse_coordinates_to_image_coordinates(
                event.pos().x(), event.pos().y(), camera_view_size, self._image_frame)
            self.v2 = (img_x, img_y)

    def mouse_release_event(self, camera_view, event):
        if self.v2 is None or self.v1 is None:
            self.set_drawing(False)
            return

        width = self.v2[0] - self.v1[0]
        height = self.v2[1] - self.v1[1]
        position = [self.v1[0] + int(width / 2), self.v1[1] + int(height / 2)]

        image_path, _ = QFileDialog.getOpenFileName()
        if image_path is None or image_path == "":
            return

        if self.is_annotation_valid(width, height):
            annotation = ImageAnnotation()
            annotation.set_position(position)
            annotation.width.set_value(abs(width))
            annotation.height.set_value(abs(height))
            annotation.image_path.set_value(image_path)
            self.annotations_model.add_annotation(annotation)

        self.set_drawing(False)

    def set_drawing(self, drawing):
        self._drawing = drawing

    @staticmethod
    def is_annotation_valid(width, height):
        return abs(width) >= ImageAnnotation.MINIMUM_WIDTH \
               and abs(height) >= ImageAnnotation.MINIMUM_HEIGHT

    def draw(self):
        if not self._drawing:
            return

        if self.annotation:
            position = sceneutil.convert_object_to_image(self.annotation.position.get_value(), self.phys_obj)
            width = self.annotation.width.get_value()
            height = self.annotation.height.get_value()
            img_path = os.path.join(
                scenemodel.current_project.base_path, self.annotation.image_path.get_value())
            image = None
            if img_path in ImageAnnotationTool.image_cache:
                image = ImageAnnotationTool.image_cache[img_path]
            else:
                image = cv2.imread(str(img_path))
                ImageAnnotationTool.image_cache[img_path] = image

            if image.shape[0] != height or image.shape[1] != width:
                image = cv2.resize(image, (width, height))

            sceneutil.draw_image_on(self._img, image, position)
        else:
            if self.v2 is None:
                return
            color = self.color
            thickness = self.thickness
            cv2.rectangle(self._img,
                          tuple(self.v1),
                          tuple(self.v2),
                          color,
                          thickness)


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
