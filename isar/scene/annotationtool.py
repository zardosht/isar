import logging
import os
from threading import Thread

import cv2
import numpy
from PyQt5.QtWidgets import QMessageBox, QFileDialog

from isar.events import eventmanager
from isar.scene import sceneutil, scenemodel
from isar.scene.annotationmodel import LineAnnotation, RectangleAnnotation, CircleAnnotation, TimerAnnotation, \
    VideoAnnotation, AudioAnnotation, ImageAnnotation, TextAnnotation, ArrowAnnotation, RelationshipAnnotation, \
    CheckboxAnnotation, ActionButtonAnnotation, CurveAnnotation, AnimationAnnotation
from isar.scene.sceneutil import Frame

logger = logging.getLogger("isar.scene.annotationtool")


class AnnotationTool:
    def __init__(self):
        self._img = None
        self._image_frame = None
        self.phys_obj = None
        self.scene_scale_factor = (1., 1.)
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


def draw_annotation(opencv_img, annotation, phys_obj=None, scene_scale_factor=(1., 1.)):
    annotation_tool = annotation_tools[annotation.__class__.__name__]
    annotation_tool.set_image(opencv_img)
    annotation_tool.phys_obj = phys_obj
    annotation_tool.scene_scale_factor = scene_scale_factor
    annotation_tool.annotation = annotation
    annotation_tool.set_drawing(True)
    annotation_tool.draw()


"""
Text
Arrow
SelectBox
Line
Circle
Rectangle
Relationship
Image
Video
Audio
Timer
ActionButton
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

        center = sceneutil.convert_object_to_image(self.annotation.center.get_value(),
                                                   self.phys_obj, self.scene_scale_factor)
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
            self.v1 = sceneutil.convert_object_to_image(v1, self.phys_obj, self.scene_scale_factor)
            v2 = [0, 0]
            v2[0] = position[0] + int(width / 2)
            v2[1] = position[1] + int(height / 2)
            self.v2 = sceneutil.convert_object_to_image(v2, self.phys_obj, self.scene_scale_factor)
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

        start = sceneutil.convert_object_to_image(self.annotation.start.get_value(),
                                                  self.phys_obj, self.scene_scale_factor)
        end = sceneutil.convert_object_to_image(self.annotation.end.get_value(), self.phys_obj,
                                                self.scene_scale_factor)

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

        position = sceneutil.convert_object_to_image(
            self.annotation.position.get_value(), self.phys_obj, self.scene_scale_factor)
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

        head = sceneutil.convert_object_to_image(self.annotation.head.get_value(),
                                                 self.phys_obj, self.scene_scale_factor)
        tail = sceneutil.convert_object_to_image(self.annotation.tail.get_value(),
                                                 self.phys_obj, self.scene_scale_factor)

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
                        tipLength=tip_length)

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

        file_path, _ = QFileDialog.getOpenFileName()
        if file_path is None or file_path == "":
            return

        if self.is_annotation_valid(width, height):
            annotation = self.create_annotation(height, file_path, position, width)
            self.annotations_model.add_annotation(annotation)

        self.set_drawing(False)

    @staticmethod
    def create_annotation(height, file_path, position, width):
        annotation = ImageAnnotation()
        annotation.set_position(position)
        annotation.width.set_value(abs(width))
        annotation.height.set_value(abs(height))
        annotation.image_path.set_value(file_path)
        return annotation

    @staticmethod
    def is_annotation_valid(width, height):
        return abs(width) >= ImageAnnotation.MINIMUM_WIDTH \
               and abs(height) >= ImageAnnotation.MINIMUM_HEIGHT

    def draw(self):
        if not self._drawing:
            return

        if self.annotation:
            self.draw_annotation()
        else:
            self.draw_size_box()

    def draw_annotation(self):
        position = sceneutil.convert_object_to_image(self.annotation.position.get_value(),
                                                     self.phys_obj, self.scene_scale_factor)
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

        if image is None:
            logger.warning("Image is None")
            return

        if image.shape[0] != height or image.shape[1] != width:
            image = cv2.resize(image, (width, height))

        sceneutil.draw_image_on(self._img, image, position)

    def draw_size_box(self):
        if self.v2 is None:
            return
        color = self.color
        thickness = self.thickness
        cv2.rectangle(self._img,
                      tuple(self.v1),
                      tuple(self.v2),
                      color,
                      thickness)


class VideoAnnotationTool(ImageAnnotationTool):
    video_cache = {}

    def __init__(self):
        super(VideoAnnotationTool, self).__init__()
        self.loading_video = False

    def mouse_press_event(self, camera_view, event):
        super().mouse_press_event(camera_view, event)

    def mouse_move_event(self, camera_view, event):
        super().mouse_move_event(camera_view, event)

    def mouse_release_event(self, camera_view, event):
        super().mouse_release_event(camera_view, event)

    def draw(self):
        super().draw()

    def draw_annotation(self):
        position = sceneutil.convert_object_to_image(self.annotation.position.get_value(),
                                                     self.phys_obj, self.scene_scale_factor)
        width = self.annotation.width.get_value()
        height = self.annotation.height.get_value()
        video_path = os.path.join(
            scenemodel.current_project.base_path, self.annotation.video_path.get_value())
        frame = None
        if video_path in VideoAnnotationTool.video_cache:
            video = VideoAnnotationTool.video_cache[video_path]
            if self.annotation.stopped:
                # set frame to the zeroth frame
                frame = video[0]
            elif self.annotation.paused:
                frame_num = self.annotation.current_frame
                frame = video[frame_num]
            else:
                frame_num = self.annotation.current_frame
                if frame_num >= len(video) and not self.annotation.loop_playback.get_value():
                    self.annotation.stopped = True
                    self.annotation.playing = False
                    self.annotation.paused = False
                    frame_num = 0
                frame = video[frame_num]
                self.annotation.current_frame += 1
                if self.annotation.current_frame >= len(video):
                    if self.annotation.loop_playback.get_value():
                        self.annotation.current_frame = 0
                    else:
                        self.annotation.playing = False
                        self.annotation.paused = False
                        self.annotation.stopped = True
        else:
            frame = cv2.imread("isar/ui/images/video_loading.png")
            if not self.loading_video:
                self.loading_video = True
                t = Thread(target=self.load_video, args=(str(video_path), ))
                t.start()

        if frame is None:
            frame = sceneutil.create_empty_image((width, height), (0, 0, 0))

        if frame.shape[0] != height or frame.shape[1] != width:
            frame = cv2.resize(frame, (width, height))
        sceneutil.draw_image_on(self._img, frame, position)

    def load_video(self, video_path):
        capture = cv2.VideoCapture(video_path)
        if capture is None:
            logger.error("ERROR: Could not open vidoe.")

        video = []
        ret = True
        while ret:
            ret, frame = capture.read()
            if ret:
                video.append(frame)
            else:
                logger.warning("WARNING: Could not read frame.")

        self.video_cache[video_path] = video
        self.loading_video = False

    @staticmethod
    def create_annotation(height, file_path, position, width):
        annotation = VideoAnnotation()
        annotation.set_position(position)
        annotation.width.set_value(abs(width))
        annotation.height.set_value(abs(height))
        annotation.video_path.set_value(file_path)
        return annotation


class ActionButtonAnnotationTool(RectangleAnnotationTool):
    def __init__(self):
        super(ActionButtonAnnotationTool, self).__init__()
        self.text = None

    def mouse_press_event(self, camera_view, event):
        super().mouse_press_event(camera_view, event)
        self.text = None

    def mouse_release_event(self, camera_view, event):
        if self.v2 is None or self.v1 is None:
            self.set_drawing(False)
            return

        width = self.v2[0] - self.v1[0]
        height = self.v2[1] - self.v1[1]
        position = [self.v1[0] + int(width / 2), self.v1[1] + int(height / 2)]

        if self.is_annotation_valid(width, height):
            annotation = ActionButtonAnnotation()
            annotation.set_position(position)
            annotation.width.set_value(abs(width))
            annotation.height.set_value(abs(height))
            self.annotations_model.add_annotation(annotation)

        self.set_drawing(False)

    def draw(self):
        if not self._drawing:
            return

        color = self.color
        thickness = self.thickness
        if self.annotation:
            position = self.annotation.position.get_value()
            width = self.annotation.width.get_value()
            height = self.annotation.height.get_value()
            v1 = [0, 0]
            v1[0] = position[0] - int(width / 2)
            v1[1] = position[1] - int(height / 2)
            self.v1 = sceneutil.convert_object_to_image(v1, self.phys_obj, self.scene_scale_factor)
            v2 = [0, 0]
            v2[0] = position[0] + int(width / 2)
            v2[1] = position[1] + int(height / 2)
            self.v2 = sceneutil.convert_object_to_image(v2, self.phys_obj, self.scene_scale_factor)
            color = self.annotation.color.get_value()
            thickness = self.annotation.thickness.get_value()

            self.text = self.annotation.text.get_value()
            font_scale = self.annotation.font_scale.get_value()
            text_color = self.annotation.text_color.get_value()
            text_thickness = self.annotation.text_thickness.get_value()

            # TODO: add font property to TextAnnotation()
            font = cv2.FONT_HERSHEY_SIMPLEX
            line_type = cv2.LINE_AA

            text_size, _ = cv2.getTextSize(self.text, font, font_scale, text_thickness)
            text_position_x = int(position[0] - (text_size[0] / 2))
            text_position_y = int(position[1] + (text_size[1] / 2))

        if self.v2 is None:
            return

        cv2.rectangle(self._img,
                      tuple(self.v1),
                      tuple(self.v2),
                      color,
                      thickness)

        if self.text is None:
            return

        cv2.putText(self._img,
                    self.text,
                    (text_position_x, text_position_y),
                    font,
                    font_scale,
                    text_color,
                    text_thickness,
                    line_type)


class SelectionTool(AnnotationTool):
    def __init__(self):
        super(SelectionTool, self).__init__()

    def mouse_press_event(self, camera_view, event):
        self.annotation = None
        self.phys_obj = None
        camera_view_size = Frame(camera_view.size().width(), camera_view.size().height())
        img_x, img_y = sceneutil.mouse_coordinates_to_image_coordinates(
            event.pos().x(), event.pos().y(), camera_view_size, self._image_frame)
        for annotation in self.annotations_model.get_all_annotations():
            if annotation.intersects_with_point((img_x, img_y)):
                self.annotation = annotation
                break

        current_scene = self.annotations_model.get_current_scene()
        scene_phys_objs = current_scene.get_physical_objects()
        for phys_obj in scene_phys_objs:
            if phys_obj.collides_with_point((img_x, img_y), self.scene_scale_factor):
                self.phys_obj = phys_obj

    def mouse_release_event(self, camera_view, event):
        scene_id = self.annotations_model.get_current_scene().name
        if self.annotation is not None:
            eventmanager.fire_selection_event(self.annotation, scene_id)
        elif self.phys_obj is not None:
            eventmanager.fire_selection_event(self.phys_obj, scene_id)


class AudioAnnotationTool(AnnotationTool):
    def __init__(self):
        super(AudioAnnotationTool, self).__init__()
        self.position = None
        self.audio_icon = cv2.imread("isar/ui/images/audio_icon.png")

    def mouse_press_event(self, camera_view, event):
        self.position = None
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
        self.position = (img_x, img_y)

    def mouse_move_event(self, camera_view, event):
        # do nothing
        pass

    def mouse_release_event(self, camera_view, event):
        if self.position is None:
            self.set_drawing(False)
            return

        file_path, _ = QFileDialog.getOpenFileName()
        if file_path is None or file_path == "":
            return

        self.annotation = AudioAnnotation()
        self.annotation.position.set_value(self.position)
        self.annotation.audio_path.set_value(file_path)
        self.annotations_model.add_annotation(self.annotation)

        self.set_drawing(False)

    def draw(self):
        if not self._drawing:
            return

        if not self.annotation:
            return

        position = sceneutil.convert_object_to_image(self.annotation.position.get_value(),
                                                     self.phys_obj, self.scene_scale_factor)
        width = self.annotation.icon_size.get_value()
        height = self.annotation.icon_size.get_value()
        audio_icon = self.audio_icon
        if audio_icon is None:
            logger.error("Audio icon is not loaded!")
            return

        if self.audio_icon.shape[0] != height or self.audio_icon.shape[1] != width:
            audio_icon = cv2.resize(self.audio_icon, (width, height))

        text = self.annotation.text.get_value()
        font_scale = self.annotation.font_scale.get_value()
        text_color = self.annotation.text_color.get_value()
        text_thickness = self.annotation.text_thickness.get_value()

        # TODO: add font property to TextAnnotation()
        font = cv2.FONT_HERSHEY_SIMPLEX
        line_type = cv2.LINE_AA

        sceneutil.draw_image_on(self._img, audio_icon, position)
        cv2.putText(self._img,
                    text,
                    position,
                    font,
                    font_scale,
                    text_color,
                    text_thickness,
                    line_type)


class TimerAnnotationTool(AnnotationTool):
    def __init__(self):
        super(TimerAnnotationTool, self).__init__()

    def mouse_press_event(self, camera_view, event):
        self.set_drawing(True)
        self.annotation = TimerAnnotation()

        # convert mouse coordinates to image coordinates
        camera_view_size = Frame(camera_view.size().width(), camera_view.size().height())
        img_x, img_y = sceneutil.mouse_coordinates_to_image_coordinates(
            event.pos().x(), event.pos().y(), camera_view_size, self._image_frame)
        self.annotation.position.set_value((img_x, img_y))

    def mouse_move_event(self, camera_view, event):
        # do nothing
        pass

    def mouse_release_event(self, camera_view, event):
        self.annotations_model.add_annotation(self.annotation)
        self.set_drawing(False)

    def draw(self):
        if not self._drawing:
            return

        if not self.annotation:
            return

        position = sceneutil.convert_object_to_image(self.annotation.position.get_value(),
                                                     self.phys_obj, self.scene_scale_factor)
        text = self.annotation.text.get_value()
        font_scale = self.annotation.font_scale.get_value()
        text_color = self.annotation.text_color.get_value()
        text_thickness = self.annotation.text_thickness.get_value()

        # TODO: add font property
        font = cv2.FONT_HERSHEY_SIMPLEX
        line_type = cv2.LINE_AA

        show_as_fraction = self.annotation.show_as_fraction.get_value()
        show_as_chart = self.annotation.show_as_chart.get_value()
        show_as_time = self.annotation.show_as_time.get_value()

        current_time = self.annotation.current_time
        duration = self.annotation.duration.get_value()

        remaining_time = duration - current_time
        minutes = remaining_time // 60
        seconds = remaining_time % 60
        remaining_time_text = str(minutes).zfill(2) + ":" + str(seconds).zfill(2)
        text_size, _ = cv2.getTextSize(remaining_time_text, font, font_scale, text_thickness)

        if show_as_fraction:
            text_size, _ = cv2.getTextSize(str(duration), font, font_scale, text_thickness)
            width = text_size[0] + 2 * text_thickness
            height = 2 * text_size[1] + 5 * text_thickness
            fraction_image = numpy.zeros((height, width, 3), numpy.uint8)
            fraction_image[:] = (255, 255, 255)

            text_size, _ = cv2.getTextSize(str(duration), font, font_scale, text_thickness)
            width = text_size[0] + 2 * text_thickness
            height = 2 * text_size[1] + 10 * text_thickness
            fraction_image = numpy.zeros((height, width, 3), numpy.uint8)
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

            sceneutil.draw_image_on(self._img, fraction_image, position,
                                    position_is_topleft=False,
                                    position_is_bottom_left=True)
            cv2.putText(self._img, text,
                        (position[0], position[1] + text_thickness + text_size[1]),
                        font, font_scale, text_color, text_thickness, line_type)

        elif show_as_chart:
            text_size, _ = cv2.getTextSize(str(duration), font, font_scale, text_thickness)
            radius = int(3 * text_size[1])

            width = 2 * radius + 2 * text_thickness
            height = 2 * radius + 2 * text_thickness
            chart_image = numpy.zeros((height, width, 3), numpy.uint8)
            chart_image[:] = (255, 255, 255)

            center = (int(width / 2), int(height / 2))
            # a circle for total duration
            cv2.ellipse(chart_image, center, (radius, radius), -90, 0, 360, (255, 0, 0), -1)
            # a circle segment on top of that for current time
            end_angle = int(current_time * (360 / duration))
            cv2.ellipse(chart_image, center, (radius, radius), -90, 0, end_angle, (0, 0, 255), -1)

            sceneutil.draw_image_on(self._img, chart_image, position,
                                    position_is_topleft=False,
                                    position_is_bottom_left=True)
            cv2.putText(self._img, text,
                        (position[0], position[1] + text_thickness + text_size[1]),
                        font, font_scale, text_color, text_thickness, line_type)

        elif show_as_time:
            remaining_time = duration - current_time
            minutes = remaining_time // 60
            seconds = remaining_time % 60
            remaining_time_text = str(minutes).zfill(2) + ":" + str(seconds).zfill(2)

            width = text_size[0] + 2 * text_thickness
            height = text_size[1] + 4 * text_thickness
            time_image = numpy.zeros((height, width, 3), numpy.uint8)
            time_image[:] = (255, 255, 255)

            cv2.putText(time_image, remaining_time_text,
                        (text_thickness, text_thickness + text_size[1]),
                        font, font_scale, text_color, text_thickness, line_type)

            sceneutil.draw_image_on(self._img, time_image, position,
                                    position_is_topleft=False,
                                    position_is_bottom_left=True)
            cv2.putText(self._img, text,
                        (position[0], position[1] + text_thickness + text_size[1]),
                        font, font_scale, text_color, text_thickness, line_type)


class CheckboxAnnotationTool(AnnotationTool):
    def __init__(self):
        super(CheckboxAnnotationTool, self).__init__()

    def mouse_press_event(self, camera_view, event):
        self.set_drawing(True)
        self.annotation = CheckboxAnnotation()

        # convert mouse coordinates to image coordinates
        camera_view_size = Frame(camera_view.size().width(), camera_view.size().height())
        img_x, img_y = sceneutil.mouse_coordinates_to_image_coordinates(
            event.pos().x(), event.pos().y(), camera_view_size, self._image_frame)
        self.annotation.position.set_value((img_x, img_y))

    def mouse_move_event(self, camera_view, event):
        # do nothing
        pass

    def mouse_release_event(self, camera_view, event):
        self.annotations_model.add_annotation(self.annotation)
        self.set_drawing(False)

    def draw(self):
        if not self._drawing:
            return

        if self.annotation is None:
            return

        position = sceneutil.convert_object_to_image(self.annotation.position.get_value(),
                                                     self.phys_obj, self.scene_scale_factor)
        color = self.annotation.color.get_value()
        thickness = self.annotation.thickness.get_value()
        size = self.annotation.size.get_value()
        v2 = (position[0] + size, position[1] + size)
        checked = self.annotation.checked.get_value()
        if checked:
            cv2.rectangle(self._img,
                          position,
                          v2,
                          color,
                          thickness)
            cv2.line(self._img, position, v2, color, thickness)
            cv2.line(self._img, (position[0], position[1] + size), (position[0] + size, position[1]), color, thickness)
        else:
            cv2.rectangle(self._img,
                      position,
                      v2,
                      color,
                      thickness)


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


class CurveAnnotationTool(AnnotationTool):
    def __init__(self):
        super(CurveAnnotationTool, self).__init__()

    def mouse_press_event(self, camera_view, event):
        self.set_drawing(True)
        self.annotation = CurveAnnotation()

        # convert mouse coordinates to image coordinates
        camera_view_size = Frame(camera_view.size().width(), camera_view.size().height())
        img_x, img_y = sceneutil.mouse_coordinates_to_image_coordinates(
            event.pos().x(), event.pos().y(), camera_view_size, self._image_frame)

        self.annotation.line_positions.append((img_x, img_y))
        self.annotation.start.set_value((img_x, img_y))
        self.annotation.set_position((img_x, img_y))

        self.compute_line_positions = []
        self.compute_line_positions.append((img_x, img_y))

    def mouse_move_event(self, camera_view, event):
        if self._drawing:
            camera_view_size = Frame(camera_view.size().width(), camera_view.size().height())
            img_x, img_y = sceneutil.mouse_coordinates_to_image_coordinates(
                event.pos().x(), event.pos().y(), camera_view_size, self._image_frame)

            self.annotation.line_positions.append((img_x, img_y))

            start = self.annotation.line_positions[len(self.annotation.line_positions) - 1]
            end = self.annotation.line_positions[len(self.annotation.line_positions) - 2]
            cv2.line(self._img, start, end, self.annotation.color.get_value(),
                     self.annotation.thickness.get_value())

            if len(self.compute_line_positions) > 0:
               self.compute_line_positions = self.compute_line_positions \
                                        + line_iterator(self.compute_line_positions.pop(), (img_x, img_y))

    def mouse_release_event(self, camera_view, event):
        camera_view_size = Frame(camera_view.size().width(), camera_view.size().height())
        img_x, img_y = sceneutil.mouse_coordinates_to_image_coordinates(
            event.pos().x(), event.pos().y(), camera_view_size, self._image_frame)

        self.annotation.line_positions.append((img_x, img_y))
        self.annotation.end.set_value((img_x, img_y))

        self.compute_line_positions = self.compute_line_positions \
                                      + line_iterator(self.compute_line_positions.pop(), (img_x, img_y))
        self.annotation.line_positions = self.compute_line_positions
        self.annotation.points.set_value(len(self.annotation.line_positions))

        if self.is_annotation_valid():
            self.annotations_model.add_annotation(self.annotation)

        self.set_drawing(False)

    def draw(self):
        if not self._drawing:
            return

        if not self.annotation:
            return

        if self.is_annotation_valid():
            if self.annotation.end.get_value() is not None:
                self.annotation.line_positions[0] = self.annotation.start.get_value()
                self.annotation.line_positions[len(self.annotation.line_positions) - 1] = self.annotation.end.get_value()
                cv2.circle(self._img, self.annotation.start.get_value(), 7,(0,255,255), -1)
                cv2.circle(self._img, self.annotation.end.get_value(), 7,(0,255,255), -1)

            if self.annotation.show_points.get_value() is False:
                for i in range(len(self.annotation.line_positions) - 1):
                    start = sceneutil.convert_object_to_image(self.annotation.line_positions[i], self.phys_obj,
                                                              self.scene_scale_factor)
                    end = sceneutil.convert_object_to_image(self.annotation.line_positions[i + 1], self.phys_obj,
                                                            self.scene_scale_factor)

                    cv2.line(self._img, start, end, self.annotation.color.get_value(),
                             self.annotation.thickness.get_value())
            else:
                self.annotation.line_points_distributed = distribute_points(self.annotation.points.get_value(), self.annotation.line_positions)
                for point in self.annotation.line_points_distributed:
                    cv2.circle(self._img, point, self.annotation.thickness.get_value(),
                               self.annotation.color.get_value(), -1)

    def is_annotation_valid(self):
        # Are there any coordinates saved?
        if len(self.annotation.line_positions) < CurveAnnotation.MINIMUM_NUMBER_POSITIONS:
            return False
        return True


class AnimationAnnotationTool(AnnotationTool):
    image_cache = {}

    def __init__(self):
        super(AnimationAnnotationTool, self).__init__()

    def mouse_press_event(self, camera_view, event):
        if scenemodel.current_project is None:
            QMessageBox.warning(None,
                                "Error",
                                "You first need to create a project to add Image, Audio, Video and Animation "
                                "annotations.")
            return

        self.set_drawing(True)
        self.annotation = AnimationAnnotation()

        # convert mouse coordinates to image coordinates
        camera_view_size = Frame(camera_view.size().width(), camera_view.size().height())
        img_x, img_y = sceneutil.mouse_coordinates_to_image_coordinates(
            event.pos().x(), event.pos().y(), camera_view_size, self._image_frame)

        self.annotation.set_position((img_x, img_y))
        self.annotation.line_start = (img_x, img_y)
        self.annotation.image_position = (img_x, img_y)

        # compute the difference between position and the mouse coordinates for moving the animation
        diff = tuple(numpy.subtract((img_x, img_y), self.annotation.position.get_value()))
        self.annotation.line_positions.append(diff)

    def mouse_move_event(self, camera_view, event):
        if self._drawing:
            camera_view_size = Frame(camera_view.size().width(), camera_view.size().height())
            img_x, img_y = sceneutil.mouse_coordinates_to_image_coordinates(
                event.pos().x(), event.pos().y(), camera_view_size, self._image_frame)

            # compute the difference for moving the animation
            diff = tuple(numpy.subtract((img_x, img_y), self.annotation.position.get_value()))
            self.annotation.line_positions.append(diff)

            start = tuple(numpy.add(self.annotation.line_positions[len(self.annotation.line_positions) - 1],
                                    self.annotation.position.get_value()))
            end = tuple(numpy.add(self.annotation.line_positions[len(self.annotation.line_positions) - 2],
                                  self.annotation.position.get_value()))
            cv2.line(self._img, start, end, self.annotation.line_color.get_value(),
                     self.annotation.line_thickness.get_value())

    def mouse_release_event(self, camera_view, event):
        camera_view_size = Frame(camera_view.size().width(), camera_view.size().height())
        img_x, img_y = sceneutil.mouse_coordinates_to_image_coordinates(
            event.pos().x(), event.pos().y(), camera_view_size, self._image_frame)

        diff = tuple(numpy.subtract((img_x, img_y), self.annotation.position.get_value()))
        self.annotation.line_positions.append(diff)

        file_path, _ = QFileDialog.getOpenFileName()
        if file_path is None or file_path == "":
            self.set_drawing(False)
            return

        self.annotation.image_path.set_value(file_path)

        if self.is_annotation_valid():
            self.annotations_model.add_annotation(self.annotation)

        self.annotation.image_shown = True
        self.set_drawing(False)

    def draw(self):
        if not self._drawing:
            return

        if not self.annotation:
            return

        if self.is_annotation_valid():
            for i in range(len(self.annotation.line_positions) - 1):
                start_add = tuple(numpy.add(self.annotation.line_positions[i], self.annotation.position.get_value()))
                start = sceneutil.convert_object_to_image(start_add, self.phys_obj, self.scene_scale_factor)

                end_add = tuple(numpy.add(self.annotation.line_positions[i + 1], self.annotation.position.get_value()))
                end = sceneutil.convert_object_to_image(end_add, self.phys_obj, self.scene_scale_factor)

                cv2.line(self._img, start, end, self.annotation.line_color.get_value(),
                         self.annotation.line_thickness.get_value())

        if self.annotation.animation_thread is None:
            self.annotation.image_position = self.annotation.position.get_value();
        self.annotation.line_start = tuple(numpy.add(self.annotation.line_positions[0], self.annotation.position.get_value()))

        if self.annotation.image_shown is True:
            self.draw_image()

    def draw_image(self):
        img_position = sceneutil.convert_object_to_image(self.annotation.image_position,
                                                         self.phys_obj, self.scene_scale_factor)
        width = self.annotation.image_width.get_value()
        height = self.annotation.image_height.get_value()
        img_position = [self.annotation.image_position[0] - int(width / 2),
                        self.annotation.image_position[1] - int(height / 2)]

        img_path = os.path.join(
            scenemodel.current_project.base_path, self.annotation.image_path.get_value())
        image = None
        if img_path in AnimationAnnotationTool.image_cache:
            image = AnimationAnnotationTool.image_cache[img_path]
        else:
            image = cv2.imread(str(img_path))
            AnimationAnnotationTool.image_cache[img_path] = image

        if image is None:
            logger.warning("Image is None")
            return

        if image.shape[0] != height or image.shape[1] != width:
            image = cv2.resize(image, (width, height))

        sceneutil.draw_image_on(self._img, image, img_position)

    def is_annotation_valid(self):
        if len(self.annotation.line_positions) < AnimationAnnotation.MINIMUM_NUMBER_POSITIONS:
            return False
        if self.annotation.image_height.get_value() < AnimationAnnotation.MINIMUM_HEIGHT \
                or self.annotation.image_width.get_value() < AnimationAnnotation.MINIMUM_WIDTH:
            return False
        return True


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
    CheckboxAnnotation.__name__: CheckboxAnnotationTool(),
    ActionButtonAnnotation.__name__: ActionButtonAnnotationTool(),
    CurveAnnotation.__name__: CurveAnnotationTool(),
    AnimationAnnotation.__name__: AnimationAnnotationTool()
}

annotation_tool_btns = {
    "line_btn": LineAnnotationTool(),
    "rectangle_btn": RectangleAnnotationTool(),
    "circle_btn": CircleAnnotationTool(),
    "select_btn": SelectionTool(),
    "check_box_btn": CheckboxAnnotationTool(),
    "text_btn": TextAnnotationTool(),
    "timer_btn": TimerAnnotationTool(),
    "video_btn": VideoAnnotationTool(),
    "audio_btn": AudioAnnotationTool(),
    "relationship_btn": RelationshipAnnotationTool(),
    "arrow_btn": ArrowAnnotationTool(),
    "image_btn": ImageAnnotationTool(),
    "action_button_btn": ActionButtonAnnotationTool(),
    "curve_btn": CurveAnnotationTool(),
    "animation_btn": AnimationAnnotationTool()
}


"""
Implementation of a method that takes two distant points and returns 
all the points between them.
Method used for smoothing the CurveAnnotation line and AnimationAnnotation line.
"""


def line_iterator(pt1, pt2):
    pt1_x = pt1[0]
    pt1_y = pt1[1]
    pt2_x = pt2[0]
    pt2_y = pt2[1]

    # difference and absolute difference between points
    # used to calculate slope and relative location between points
    d_x = pt2_x - pt1_x
    d_y = pt2_y - pt1_y
    d_xa = numpy.abs(d_x)
    d_ya = numpy.abs(d_y)

    # predefine numpy array for output based on distance between points
    iterator = numpy.empty(shape=(numpy.maximum(d_ya, d_xa), 2), dtype=numpy.int)

    # obtain coordinates along the line
    neg_y = pt1_y > pt2_y
    neg_x = pt1_x > pt2_x
    if pt1_x == pt2_x:
        # vertical line segment
        iterator[:, 0] = pt1_x
        if neg_y:
            iterator[:, 1] = numpy.arange(pt1_y - 1, pt1_y - d_ya - 1, -1)
        else:
            iterator[:, 1] = numpy.arange(pt1_y + 1, pt1_y + d_ya + 1)
    elif pt1_y == pt2_y:
        # horizontal line segment
        iterator[:, 1] = pt1_y
        if neg_x:
            iterator[:, 0] = numpy.arange(pt1_x - 1, pt1_x - d_xa - 1, -1)
        else:
            iterator[:, 0] = numpy.arange(pt1_x + 1, pt1_x + d_xa + 1)
    else:
        # diagonal line segment
        steep_slope = d_ya > d_xa
        if steep_slope:
            slope = d_x / d_y
            if neg_y:
                iterator[:, 1] = numpy.arange(pt1_y - 1, pt1_y - d_ya - 1, -1)
            else:
                iterator[:, 1] = numpy.arange(pt1_y + 1, pt1_y + d_ya + 1)
            iterator[:, 0] = (slope * (iterator[:, 1] - pt1_y)) + pt1_x
        else:
            slope = d_y / d_x
            if neg_x:
                iterator[:, 0] = numpy.arange(pt1_x - 1, pt1_x - d_xa - 1, -1)
            else:
                iterator[:, 0] = numpy.arange(pt1_x + 1, pt1_x + d_xa + 1)
            iterator[:, 1] = (slope * (iterator[:, 0] - pt1_x)).astype(numpy.int) + pt1_y

    line_positions = []
    for position in iterator:
        pos = (int(position[0]),int(position[1]))
        line_positions.append(tuple(pos))
    return line_positions


"""
Implementation of a method that takes line positions along a curve and distributes the points.
"""


def distribute_points(distribution, line_positions):
    if distribution >= len(line_positions):
        return line_positions

    p_x = []
    p_y = []
    for point in line_positions:
        p_x.append(point[0])
        p_y.append(point[1])

    # equally spaced in arc length
    distribution = numpy.transpose(numpy.linspace(0, 1, distribution))

    # number of points on the curve
    n = len(p_x)
    matrix_xy = numpy.array((p_x, p_y)).T

    # compute the chordal arc length of each segment.
    chordal = (numpy.sum(numpy.diff(matrix_xy, axis=0) ** 2, axis=1)) ** (1 / 2)

    # normalize the arc lengths to a unit total
    chordal = chordal / numpy.sum(chordal)

    # cumulative arc length
    cumulative = numpy.append(0, numpy.cumsum(chordal))

    # bin index in which each N is in
    bin_index = numpy.digitize(distribution, cumulative)

    # catch any problems at the ends
    bin_index[numpy.where(numpy.bitwise_or(bin_index <= 0, (distribution <= 0)))] = 1
    bin_index[numpy.where(numpy.bitwise_or(bin_index >= n, (distribution >= 1)))] = n - 1

    s = numpy.divide((distribution - cumulative[bin_index]), chordal[bin_index - 1])
    distributed_points = matrix_xy[bin_index, :] + numpy.multiply(
        (matrix_xy[bin_index, :] - matrix_xy[bin_index - 1, :]), (numpy.vstack([s] * 2)).T)

    return_positions = []
    for position in distributed_points:
        pos = (int(position[0]), int(position[1]))
        return_positions.append(tuple(pos))

    return return_positions
