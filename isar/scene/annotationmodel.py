import logging
import math
import os
import shutil
import time
import traceback
from ast import literal_eval
from threading import Thread, Event
from typing import List

import numpy
from PyQt5 import QtCore
from PyQt5.QtCore import QAbstractListModel, Qt, QModelIndex, QAbstractTableModel, pyqtSignal
from PyQt5.QtWidgets import QComboBox, QFileDialog, QStyledItemDelegate, QWidget, QHBoxLayout, \
    QPushButton, QLabel, QVBoxLayout, QSizePolicy

from isar import ApplicationMode
from isar.events import eventmanager
from isar.scene import sceneutil, scenemodel, audioutil
from isar.scene.physicalobjectmodel import PhysicalObject
from isar.scene.scenemodel import Scene

logger = logging.getLogger("isar.scene.annotationmodel")


class AnnotationsModel(QAbstractListModel):
    editCompleted = QtCore.pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.current_annotation = None
        self.__scene: Scene = None
        self.__annotations = None

    def set_scene(self, scene):
        self.__scene = scene
        self.__annotations = scene.get_all_annotations()
        if len(self.__annotations) > 0:
            self.current_annotation = self.__annotations[0]
        else:
            self.current_annotation = None

        if ApplicationMode.AUTHORING:
            self.update_annotation_counters()

        self.endResetModel()

    def update_annotation_counters(self):
        global annotation_counters
        for annotation_class_name in annotation_counters:
            annotation_counters[annotation_class_name] = 0

        for annotation in self.__annotations:
            annotation_counters[annotation.__class__.__name__] += 1

    def rowCount(self, parent=None):
        if self.__annotations is None:
            return 0

        return len(self.__annotations)

    def data(self, index, role):
        if self.__annotations is None:
            return

        if role == QtCore.Qt.DisplayRole:
            return self.__annotations[index.row()].name

    def setData(self, index, value, role):
        if self.__annotations is None:
            return

        if role == Qt.EditRole:
            annotation = self.__annotations[index.row()]
            new_name = annotation.name
            try:
                taken_names = [annot.name for annot in self.__annotations]
                if sceneutil.is_valid_name(str(value), taken_names):
                    new_name = str(value)
            except Exception as e:
                print("Error editing annotation name", e)
                return False

            annotation.name = new_name
            annotation.id = self.__scene.name + sceneutil.ANNOTATION_ID_SEPARATOR + new_name
            self.editCompleted.emit(new_name)

        return True

    def flags(self, index):
        return Qt.ItemIsSelectable | Qt.ItemIsEditable | Qt.ItemIsEnabled

    def add_annotation(self, new_annotation):
        if self.__scene is None:
            return

        at_row = self.rowCount(None) + 1
        self.beginInsertRows(QModelIndex(), at_row, at_row)
        self.insertRow(at_row)
        class_name = new_annotation.__class__.__name__
        new_annotation.name = new_annotation.__class__.__name__ + str(annotation_counters[class_name])
        new_annotation.id = self.__scene.name + sceneutil.ANNOTATION_ID_SEPARATOR + new_annotation.name
        new_annotation.scene = self.__scene
        self.__scene.add_annotation(new_annotation)
        self.__annotations = self.__scene.get_all_annotations()

        annotation_counters[class_name] += 1
        self.current_annotation = new_annotation
        self.endInsertRows()

    def delete_annotation_at(self, selected_index):
        if self.__scene is None:
            return

        if len(self.__annotations) == 0:  # keep at least one scene
            return

        if len(self.__annotations) <= selected_index.row():
            return

        self.beginRemoveRows(selected_index, selected_index.row(), selected_index.row())

        annotation = self.__annotations[selected_index.row()]
        # annotation.owner = None
        annotation.delete()
        self.__annotations = self.__scene.get_all_annotations()

        self.current_annotation = None
        self.removeRow(selected_index.row())
        self.endRemoveRows()

    def delete_annotation(self, annotation):
        if self.__scene is None:
            return

        if len(self.__annotations) == 0:  # keep at least one scene
            return

        # annotation.owner = None
        annotation.delete()
        self.__annotations = self.__scene.get_all_annotations()

        self.current_annotation = None
        self.update_view()

    def update_view(self, index=None):
        if index is None:
            if self.__scene is not None:
                self.__annotations = self.__scene.get_all_annotations()
                self.current_annotation = None
            self.endResetModel()
        else:
            self.dataChanged.emit(index, index, [Qt.DisplayRole])

    def set_current_annotation(self, selected_index):
        if self.__annotations is None:
            return

        if len(self.__annotations) == 0:
            return

        if selected_index is None:
            return

        if selected_index.row() == -1:
            return

        self.current_annotation = self.__annotations[selected_index.row()]

    def get_annotation_at(self, index: QModelIndex):
        if self.__annotations is None or len(self.__annotations) == 0:
            return None

        if index is None:
            return None

        if not index.isValid():
            return None

        return self.__annotations[index.row()]

    def get_all_annotations(self):
        if self.__annotations:
            return tuple(self.__annotations)
        else:
            return ()

    def get_annotation_by_name(self, name):
        for annotation in self.get_all_annotations():
            if annotation.name == name:
                return annotation

    def get_annotation_by_id(self, id):
        if id is None:
            return None
        full_id = id
        if not full_id.startswith(self.__scene.name):
            full_id = self.__scene.name + sceneutil.ANNOTATION_ID_SEPARATOR + id

        for annotation in self.get_all_annotations():
            if annotation.id == id:
                return annotation

    def get_scene_annotations(self):
        if self.__scene:
            return self.__scene.get_scene_annotations()
        else:
            return ()

    def get_physical_object_annotations(self, phys_obj):
        if self.__scene:
            return self.__scene.get_physical_object_annotations()
        else:
            return ()

    def get_current_scene(self):
        return self.__scene


class Annotation:
    def __init__(self):
        self.name = "Annotation"
        self.id = "id"
        self.scene = None
        # Owner of  an annotation is either the scene or a physical object. An annotation can have only one owner.
        # self.owner = None

        self.properties: List[AnnotationProperty] = []

        self.position = IntTupleAnnotationProperty("Position", (0, 0), self, self.set_position.__name__)
        self.properties.append(self.position)

        self.attached_to = PhysicalObjectAnnotationProperty("Attach To", None, self, self.set_attached_to.__name__)
        self.properties.append(self.attached_to)

        self.update_orientation = BooleanAnnotationProperty("Update Orientation", False, self)
        self.properties.append(self.update_orientation)

        self.show = BooleanAnnotationProperty("Show", True, self)
        self.properties.append(self.show)

        # TODO: For later if we want to draw annotations based on their selection state.
        self.is_selected = False
        self.is_selectable = False

    def set_position(self, position):
        # must be implemented by subclasses if needed.
        self.position._value = position
        return True

    def set_attached_to(self, phys_obj):
        old_phys_obj = self.attached_to.get_value()
        if old_phys_obj is not None and phys_obj == old_phys_obj:
            return False

        if isinstance(phys_obj, PhysicalObject):
            phys_obj.add_annotation(self)
            self.attached_to._value = phys_obj
            self.scene.remove_annotation(self)

            if old_phys_obj is not None:
                old_phys_obj.remove_annotation(self)

            self.set_position((0, 0))
            return True

        elif phys_obj is None:
            self.attached_to._value = None
            self.scene.add_annotation(self)

            if old_phys_obj is not None:
                old_phys_obj.remove_annotation(self)

            self.set_position((0, 0))
            return True

    def delete(self):
        self.set_attached_to(None)
        for prop in self.properties:
            prop.annotation = None
            prop._value = None
        self.properties.clear()
        self.scene.delete_annotation(self)
        self.scene = None

    def intersects_with_point(self, point):
        return False

    def select(self):
        self.on_select()

    def on_select(self):
        pass

    def reset_runtime_state(self):
        # runtime state of an annotation are those attributes that are not AnnotationProperty,
        # and change during runtime. For example the "stopped" or "playing" attribute of a VideoAnnotation.
        # The value of these attributes are persisted. They must be reset however, when the project is loaded.
        self.is_selected = False

    def __str__(self):
        return self.id


"""
Text
Arrow
Checkbox
Line
Circle
Rectangle
Relationship
Image
Video
Audio
Timer
ActionButton
Curve
Animation
FeedbackAnnotation
ObjectAreaAnnotation
"""


class TextAnnotation(Annotation):
    DEFAULT_TEXT = "[Text...]"

    def __init__(self):
        super().__init__()
        self.text = StringAnnotationProperty("Text", TextAnnotation.DEFAULT_TEXT, self)
        self.properties.append(self.text)

        self.color = ColorAnnotationProperty("Color", (0, 255, 0), self)
        self.properties.append(self.color)

        self.thickness = IntAnnotationProperty("Thickness", 3, self)
        self.properties.append(self.thickness)

        self.font_scale = FloatAnnotationProperty("Font Scale", 1.5, self)
        self.properties.append(self.font_scale)


class ArrowAnnotation(Annotation):
    DEFAULT_TEXT = "[Text...]"
    MINIMUM_LENGTH = 15

    def __init__(self):
        super().__init__()
        self.text = StringAnnotationProperty("Text", ArrowAnnotation.DEFAULT_TEXT, self)
        self.properties.append(self.text)

        self.text_thickness = IntAnnotationProperty("Text Thickness", 3, self)
        self.properties.append(self.text_thickness)

        self.font_scale = FloatAnnotationProperty("Font Scale", 1.5, self)
        self.properties.append(self.font_scale)

        self.text_color = ColorAnnotationProperty("Text Color", (0, 255, 255), self)
        self.properties.append(self.text_color)

        self.head = IntTupleAnnotationProperty("Head", [0, 0], self, self.set_head.__name__)
        self.properties.append(self.head)

        self.tail = IntTupleAnnotationProperty("Tail", None, self)
        self.properties.append(self.tail)

        self.thickness = IntAnnotationProperty("Thickness", 3, self)
        self.properties.append(self.thickness)

        self.color = ColorAnnotationProperty("Color", (0, 255, 255), self)
        self.properties.append(self.color)

        self.tip_length = FloatAnnotationProperty("Tip Lenght", 0.1, self)
        self.properties.append(self.tip_length)

    def set_position(self, position):
        self.position._value = position
        self.head._value = position
        return True

    def set_head(self, head):
        self.head._value = head
        self.position._value = head
        return True


class LineAnnotation(Annotation):
    MINIMUM_LENGTH = 10

    def __init__(self):
        super().__init__()

        self.start = IntTupleAnnotationProperty("Start", [0, 0], self, self.set_start.__name__)
        self.properties.append(self.start)

        self.end = IntTupleAnnotationProperty("End", None, self)
        self.properties.append(self.end)

        self.thickness = IntAnnotationProperty("Thickness", 3, self)
        self.properties.append(self.thickness)

        self.color = ColorAnnotationProperty("Color", (0, 255, 255), self)
        self.properties.append(self.color)

    def set_position(self, position):
        self.position._value = position
        self.start._value = position
        return True

    def set_start(self, start):
        self.start._value = start
        self.position._value = start
        return True


class RectangleAnnotation(Annotation):
    MINIMUM_WIDTH = 10
    MINIMUM_HEIGHT = 10

    def __init__(self):
        super(RectangleAnnotation, self).__init__()

        self.color = ColorAnnotationProperty("Color", (255, 0, 255), self)
        self.properties.append(self.color)

        self.thickness = IntAnnotationProperty("Thickness", 3, self)
        self.properties.append(self.thickness)

        self.width = IntAnnotationProperty("Width", 5, self)
        self.properties.append(self.width)

        self.height = IntAnnotationProperty("Height", 5, self)
        self.properties.append(self.height)

        self.is_selectable = True

    def intersects_with_point(self, point):
        position = self.position.get_value()
        width = self.width.get_value()
        height = self.height.get_value()
        return position[0] - int(width / 2) <= point[0] <= position[0] + int(width / 2) and \
            position[1] - int(height / 2) <= point[1] <= position[1] + int(height / 2)


class ObjectAreaAnnotation(RectangleAnnotation):
    def __init__(self):
        super().__init__()
        self.is_selectable = False


class CircleAnnotation(Annotation):
    MINIMUM_RADIUS = 5

    def __init__(self):
        super(CircleAnnotation, self).__init__()

        self.color = ColorAnnotationProperty("Color", (125, 125, 255), self)
        self.properties.append(self.color)

        self.center = IntTupleAnnotationProperty("Center", [0, 0], self, self.set_center.__name__)
        self.properties.append(self.center)

        self.radius = IntAnnotationProperty("Radius", None, self)
        self.properties.append(self.radius)

        self.thickness = IntAnnotationProperty("Thickness", 3, self)
        self.properties.append(self.thickness)

        self.is_selectable = True

    def set_position(self, position):
        self.position._value = position
        self.center._value = position
        return True

    def set_center(self, center):
        self.center._value = center
        self.position._value = center
        return True

    def intersects_with_point(self, point):
        position = self.position.get_value()
        distance = math.sqrt(math.pow((point[0] - position[0]), 2.0) + math.pow((point[0] - position[0]), 2.0))
        return distance <= self.radius.get_value()


class ImageAnnotation(Annotation):
    MINIMUM_WIDTH = 30
    MINIMUM_HEIGHT = 30

    def __init__(self):
        super(ImageAnnotation, self).__init__()

        self.image_path = FilePathAnnotationProperty("ImageFilename", None, self)
        self.properties.append(self.image_path)

        self.width = IntAnnotationProperty("Width", 5, self)
        self.properties.append(self.width)

        self.height = IntAnnotationProperty("Height", 5, self)
        self.properties.append(self.height)

        self.keep_aspect_ratio = BooleanAnnotationProperty("Keep Aspect Ratio", True, self)
        self.properties.append(self.keep_aspect_ratio)

        self.is_selectable = True

    def intersects_with_point(self, point):
        position = self.position.get_value()
        width = self.width.get_value()
        height = self.height.get_value()
        return position[0] <= point[0] <= position[0] + width and \
               position[1] <= point[1] <= position[1] + height

    def reset_runtime_state(self):
        self.is_selectable = True


class VideoAnnotation(Annotation):
    def __init__(self):
        super(VideoAnnotation, self).__init__()

        self.video_path = FilePathAnnotationProperty("VideoFilename", None, self)
        self.properties.append(self.video_path)

        self.width = IntAnnotationProperty("Width", 5, self)
        self.properties.append(self.width)

        self.height = IntAnnotationProperty("Height", 5, self)
        self.properties.append(self.height)

        self.keep_aspect_ratio = BooleanAnnotationProperty("Keep Aspect Ratio", True, self)
        self.properties.append(self.keep_aspect_ratio)

        self.loop_playback = BooleanAnnotationProperty("Loop Playback", False, self)
        self.properties.append(self.loop_playback)

        self.stopped = False
        self.playing = True
        self.paused = False
        self.current_frame = 0

    def reset_runtime_state(self):
        super().reset_runtime_state()
        self.stopped = False
        self.playing = True
        self.paused = False
        self.current_frame = 0

    def intersects_with_point(self, point):
        if point is None:
            return False

        position = self.position.get_value()
        if position is None:
            return False

        width = self.width.get_value()
        height = self.height.get_value()
        return position[0] <= point[0] <= position[0] + width and \
               position[1] <= point[1] <= position[1] + height

    def on_select(self):
        # TODO: Actually the toggling of play mode upon selection should happen
        #  when we are in ApplicationMode.EXECUTION
        #  Generally, the behavior of annotations upon selection, should be defined
        #  depending on if we are in AUTHORING or EXECUTION mode.
        if self.playing:
            self.paused = True
            self.playing = False
            self.stopped = False
        elif self.stopped:
            self.current_frame = 0
            self.playing = True
            self.paused = False
            self.stopped = False
        elif self.paused:
            self.playing = True
            self.paused = False
            self.stopped = False


class ActionButtonAnnotation(RectangleAnnotation):
    DEFAULT_TEXT = "Action"

    def __init__(self):
        super().__init__()
        self.text = StringAnnotationProperty("Text", ActionButtonAnnotation.DEFAULT_TEXT, self)
        self.properties.append(self.text)

        self.text_thickness = IntAnnotationProperty("Text Thickness", 3, self)
        self.properties.append(self.text_thickness)

        self.font_scale = FloatAnnotationProperty("Font Scale", 1.0, self)
        self.properties.append(self.font_scale)

        self.text_color = ColorAnnotationProperty("Text Color", (0, 255, 255), self)
        self.properties.append(self.text_color)

        # Actions must have been created up front in the action creator.
        self.on_select_action = ActionAnnotationProperty("On Select", None, self)
        self.properties.append(self.on_select_action)

        self.is_selectable = True

    def intersects_with_point(self, point):
        position = self.position.get_value()
        if position is None:
            return False

        width = self.width.get_value()
        height = self.height.get_value()
        return (position[0] - int(width / 2)) <= point[0] <= (position[0] + int(width / 2)) and \
               (position[1] - int(height / 2)) <= point[1] <= (position[1] + int(height / 2))

    def reset_runtime_state(self):
        self.is_selectable = True

    def on_select(self):
        logger.info("Action Button Selected -------------------------------<><><><><><><<<<<<<<<")


class CurveAnnotation(Annotation):
    MINIMUM_NUMBER_POSITIONS = 7
    RADIUS = 10

    def __init__(self):
        super(CurveAnnotation, self).__init__()

        self.start = IntTupleAnnotationProperty("Start", None, self)
        self.properties.append(self.start)

        self.end = IntTupleAnnotationProperty("End", None, self)
        self.properties.append(self.end)

        self.points = IntAnnotationProperty("Points", None, self, self.set_points.__name__)
        self.properties.append(self.points)

        self.points_color = ColorAnnotationProperty("Points color", (0, 0, 0), self)
        self.properties.append(self.points_color)

        self.points_radius = IntAnnotationProperty("Points radius", 2, self)
        self.properties.append(self.points_radius)

        self.start_stop_color = ColorAnnotationProperty("Start/Stop color", (0, 255, 255), self)
        self.properties.append(self.start_stop_color)

        self.start_stop_radius = IntAnnotationProperty("Start/Stop radius", 7, self)
        self.properties.append(self.start_stop_radius)

        self.line_points = []
        self.line_points_distributed = []

        self.exercise = None

    def set_points(self, value):
        if value <= len(self.line_points):
            self.points._value = value
            return True
        return False

    def intersects_with_point(self, point):
        if self.exercise is not None:
            if in_circle(point, self.start.get_value(), CurveAnnotation.RADIUS) and not self.exercise.running:
                self.exercise.register_points.append(point)
                self.exercise.start()

            if in_circle(point, self.end.get_value(), CurveAnnotation.RADIUS) and self.exercise.running:
                self.exercise.register_points.append(point)
                self.exercise.stop()


"""
Defining method which returns true or false if the point is in the radius from the center
"""


def in_circle(point, center, radius):
    return ((point[0] - center[0]) * (point[0] - center[0]) +
            (point[1] - center[1]) * (point[1] - center[1]) <= radius * radius)


class AnimationAnnotation(Annotation):
    MINIMUM_NUMBER_POSITIONS = 5
    MINIMUM_WIDTH = 20
    MINIMUM_HEIGHT = 20

    def __init__(self):
        super(AnimationAnnotation, self).__init__()

        self.line_color = ColorAnnotationProperty("Line Color", (0, 0, 0), self)
        self.properties.append(self.line_color)

        self.line_thickness = IntAnnotationProperty("Line Thickness", 2, self)
        self.properties.append(self.line_thickness)

        self.image_path = FilePathAnnotationProperty("Image Filename", None, self)
        self.properties.append(self.image_path)

        self.image_width = IntAnnotationProperty("Image Width", 30, self)
        self.properties.append(self.image_width)

        self.image_height = IntAnnotationProperty("Image Height", 30, self)
        self.properties.append(self.image_height)

        self.animation_speed = IntAnnotationProperty("Animation Speed", 2, self)
        self.properties.append(self.animation_speed)

        self.loop = BooleanAnnotationProperty("Loop", False, self)
        self.properties.append(self.loop)

        self.line_points = []
        self.line_start = None
        self.image_position = None
        self.image_shown = False
        self.animation_thread = None

        self.exercise = None

    def __getstate__(self):
        state = self.__dict__.copy()
        del state["animation_thread"]
        return state

    def __setstate__(self, state):
        self.__init__()
        self.__dict__.update(state)

    def intersects_with_point(self, point):
        position = self.image_position
        width = self.image_width.get_value()
        height = self.image_height.get_value()
        return position[0] <= point[0] <= position[0] + width and \
               position[1] <= point[1] <= position[1] + height

    def reset_runtime_state(self):
        self.image_position = self.line_start
        self.image_shown = True

    def on_select(self):
        logger.info("On Select.")
        self.image_shown = False
        if self.animation_thread is not None:
            self.animation_thread.stop()
            self.animation_thread = None

    def start(self):
        logger.info("Start animation.")
        if self.animation_thread is not None \
                and self.animation_thread.is_alive():
            return

        self.image_shown = True
        self.image_position = self.line_start
        self.animation_thread = AnimationThread(self)
        self.animation_thread.start()

    def stop(self):
        logger.info("Stop animation.")
        self.image_shown = True
        self.image_position = self.line_start
        if self.animation_thread is not None:
            self.animation_thread.stop()
            self.animation_thread = None


class AnimationThread(Thread):
    def __init__(self, animation_annotation):
        super().__init__(name="AnimationThread")
        self.animation_annotation = animation_annotation
        self.image_positions = numpy.add(self.animation_annotation.line_points,
                                         self.animation_annotation.position.get_value())
        self.stop_event = Event()
        # TODO: compute the speed differently because of to many points
        # self.speed = 1 - self.animation_annotation.animation_speed.get_value() / 10 + 0.1
        self.speed = 1 / self.animation_annotation.animation_speed.get_value()
        self.loop_direction = False

    def run(self):
        if self.animation_annotation.loop.get_value() is False:
            for point in self.image_positions:
                self.animation_annotation.image_position = tuple(point)
                time.sleep(self.speed)
        else:
            while self.stop_event.is_set() is False:
                if self.loop_direction is False:
                    for point in self.image_positions:
                        self.animation_annotation.image_position = tuple(point)
                        time.sleep(self.speed)
                    self.loop_direction = True

                if self.loop_direction is True:
                    for point in reversed(self.image_positions):
                        self.animation_annotation.image_position = tuple(point)
                        time.sleep(self.speed)
                    self.loop_direction = False
        logger.info("Animation thread finished.")

    def stop(self):
        self.stop_event.set()


class AudioAnnotation(Annotation):
    DEFAULT_TEXT = "--"

    def __init__(self):
        super().__init__()

        self.audio_path = FilePathAnnotationProperty("Audio Filename", None, self, self.set_audio_path.__name__)
        self.properties.append(self.audio_path)

        self.icon_size = IntAnnotationProperty("Icon Size", 30, self)
        self.properties.append(self.icon_size)

        self.text = StringAnnotationProperty("Text", AudioAnnotation.DEFAULT_TEXT, self)
        self.properties.append(self.text)

        self.text_thickness = IntAnnotationProperty("Text Thickness", 1, self)
        self.properties.append(self.text_thickness)

        self.font_scale = FloatAnnotationProperty("Font Scale", .3, self)
        self.properties.append(self.font_scale)

        self.text_color = ColorAnnotationProperty("Text Color", (0, 0, 0), self)
        self.properties.append(self.text_color)

        self.loop_playback = BooleanAnnotationProperty("Loop Playback", False, self)
        self.properties.append(self.loop_playback)

        self.stopped = False
        self.playing = True

    def set_audio_path(self, value):
        self.audio_path._value = value
        self.text._value = value
        return True

    def intersects_with_point(self, point):
        position = self.position.get_value()
        width = self.icon_size.get_value()
        height = self.icon_size.get_value()
        return position[0] <= point[0] <= position[0] + width and \
               position[1] <= point[1] <= position[1] + height

    def reset_runtime_state(self):
        super().reset_runtime_state()
        self.stopped = True
        self.playing = False

    def on_select(self):
        # TODO: Actually the toggling of play mode upon selection should happen
        #  when we are in ApplicationMode.EXECUTION
        #  Generally, the bahavior of annotations upon selection, should be defined
        #  depending on if we are in AUTHORING or EXECUTION mode.
        if self.playing:
            self.playing = False
            self.stopped = True
            self.stop()
        elif self.stopped:
            self.playing = True
            self.stopped = False
            self.play()

    def play(self):
        audioutil.play(self.audio_path.get_value(), self.loop_playback.get_value())

    def stop(self):
        audioutil.stop(self.audio_path.get_value())


class TimerAnnotation(Annotation):
    MAX_TIMER_DURATION = 3600

    def __init__(self):
        super().__init__()

        # duration in seconds
        self.duration = IntAnnotationProperty("Duration", 60, self, self.set_duration.__name__)
        self.properties.append(self.duration)

        # if True will show as HH:MM:SS, otherwise simply the duration tick
        self.show_as_time = BooleanAnnotationProperty("Show as Time", False, self, self.set_show_as_time.__name__)
        self.properties.append(self.show_as_time)

        # if True will show as a pie chart, otherwise simply the duration tick
        self.show_as_chart = BooleanAnnotationProperty("Show as Chart", False, self, self.set_show_as_chart.__name__)
        self.properties.append(self.show_as_chart)

        # if True will show as HH:MM:SS, otherwise simply the duration tick
        self.show_as_fraction = BooleanAnnotationProperty("Show as Fraction", True, self,
                                                          self.set_show_as_fraction.__name__)
        self.properties.append(self.show_as_fraction)

        self.text = StringAnnotationProperty("Text", AudioAnnotation.DEFAULT_TEXT, self)
        self.properties.append(self.text)

        self.text_thickness = IntAnnotationProperty("Text Thickness", 1, self)
        self.properties.append(self.text_thickness)

        self.font_scale = FloatAnnotationProperty("Font Scale", .5, self)
        self.properties.append(self.font_scale)

        self.text_color = ColorAnnotationProperty("Text Color", (0, 0, 0), self)
        self.properties.append(self.text_color)

        # sends timer tick events every X seconds. If set to -1 does not send timer tick events.
        self.tick_interval = IntAnnotationProperty("Tick Interval", 1, self, self.set_tick_interval.__name__)
        self.properties.append(self.tick_interval)

        # a timer can also have up to three timeout events at specific given times.
        # If set to -1, this timeout is igonred. If set to a value, the timer sends a TimerTimeoutEvent at
        # the given time.
        self.timeout_1 = IntAnnotationProperty("Timeout 1", -1, self, self.set_timeout_1.__name__)
        self.properties.append(self.timeout_1)

        self.timeout_2 = IntAnnotationProperty("Timeout 2", -1, self, self.set_timeout_2.__name__)
        self.properties.append(self.timeout_2)

        self.timeout_3 = IntAnnotationProperty("Timeout 3", -1, self, self.set_timeout_3.__name__)
        self.properties.append(self.timeout_3)

        self.current_time = 0
        self.timer_thread = None

        self.timer_finish_listeners = []

    def add_timer_finished_listener(self, listener):
        self.timer_finish_listeners.append(listener)

    def set_show_as_chart(self, value):
        self.show_as_chart._value = value
        if value:
            self.show_as_time._value = False
            self.show_as_fraction._value = False
        else:
            self.show_as_time._value = False
            self.show_as_fraction._value = True
        return True

    def set_show_as_time(self, value):
        self.show_as_time._value = value
        if value:
            self.show_as_chart._value = False
            self.show_as_fraction._value = False
        else:
            self.show_as_chart._value = False
            self.show_as_fraction._value = True
        return True

    def set_show_as_fraction(self, value):
        if value:
            self.show_as_fraction._value = value
            self.show_as_time._value = False
            self.show_as_chart._value = False
            return True
        else:
            # we must have at least a representation equal true
            return False

    def set_duration(self, value):
        if value <= TimerAnnotation.MAX_TIMER_DURATION:
            self.duration._value = value
            return True
        return False

    def set_tick_interval(self, value):
        if value <= self.duration.get_value():
            self.tick_interval._value = value
            return True
        return False

    def set_timeout_1(self, value):
        if value <= self.duration.get_value():
            self.timeout_1._value = value
            return True
        return False

    def set_timeout_2(self, value):
        if value <= self.duration.get_value():
            self.timeout_2._value = value
            return True
        return False

    def set_timeout_3(self, value):
        if value <= self.duration.get_value():
            self.timeout_3._value = value
            return True
        return False

    def reset_runtime_state(self):
        self.current_time = 0

    def __getstate__(self):
        state = self.__dict__.copy()
        del state["timer_thread"]
        return state

    def __setstate__(self, state):
        self.__init__()
        self.__dict__.update(state)

    def start(self):
        if self.timer_thread is not None \
                and self.timer_thread.is_alive():
            return

        self.current_time = 0
        self.timer_thread = TimerThread(self)
        self.timer_thread.start()

    def stop(self):
        if self.timer_thread is not None:
            self.timer_thread.stop()
            self.timer_thread = None

    def reset(self):
        self.stop()
        self.current_time = 0


class TimerThread(Thread):
    # I had to add this class because of the weired Lock exception I got,
    # when the timer thread was inside the TimerAnnotation class
    def __init__(self, timer_annotation):
        super().__init__(name="TimerThread")
        self.timer_annotation = timer_annotation
        self.scene = self.timer_annotation.scene
        self.stop_event = Event()

    def run(self):
        stopped_before_finish = False
        while self.timer_annotation.current_time < self.timer_annotation.duration.get_value():
            if self.stop_event.is_set():
                stopped_before_finish = True
                break

            self.timer_annotation.current_time += 1
            if (self.timer_annotation.current_time % self.timer_annotation.tick_interval.get_value()) == 0:
                eventmanager.fire_timer_tick_event(self.timer_annotation,
                                                   self.timer_annotation.current_time,
                                                   self.scene.name)

            if self.timer_annotation.current_time == self.timer_annotation.timeout_1.get_value():
                eventmanager.fire_timer_timeout1_event(self.timer_annotation,
                                                       self.timer_annotation.current_time,
                                                       self.scene.name)

            if self.timer_annotation.current_time == self.timer_annotation.timeout_2.get_value():
                eventmanager.fire_timer_timeout2_event(self.timer_annotation,
                                                       self.timer_annotation.current_time,
                                                       self.scene.name)

            if self.timer_annotation.current_time == self.timer_annotation.timeout_3.get_value():
                eventmanager.fire_timer_timeout3_event(self.timer_annotation,
                                                       self.timer_annotation.current_time,
                                                       self.scene.name)

            time.sleep(1)

        if not stopped_before_finish:
            eventmanager.fire_timer_finished_event(self.timer_annotation, self.scene.name)
            for listener in self.timer_annotation.timer_finish_listeners:
                listener.on_timer_finished()

    def stop(self):
        self.stop_event.set()


class CheckboxAnnotation(Annotation):
    def __init__(self):
        super().__init__()

        self.size = IntAnnotationProperty("Size", 50, self)
        self.properties.append(self.size)

        self.color = ColorAnnotationProperty("Color", (255, 0, 255), self)
        self.properties.append(self.color)

        self.thickness = IntAnnotationProperty("Thickness", 3, self)
        self.properties.append(self.thickness)

        self.checked = BooleanAnnotationProperty("Checked", False, self)
        self.properties.append(self.checked)

    def intersects_with_point(self, point):
        position = self.position.get_value()
        if position is None or point is None:
            return False

        width = self.size.get_value()
        height = self.size.get_value()
        return position[0] <= point[0] <= position[0] + width and \
               position[1] <= point[1] <= position[1] + height

    def on_select(self):
        # TODO: Actually the toggling of play mode upon selection should happen
        #  when we are in ApplicationMode.EXECUTION
        #  Generally, the bahavior of annotations upon selection, should be defined
        #  depending on if we are in AUTHORING or EXECUTION mode.
        was_checked = self.checked.get_value()
        self.checked.set_value(not was_checked)
        if not was_checked:
            # the checkbox is now checked
            eventmanager.fire_checkbox_checked_event(self, self.scene.name)
        else:
            # the checkbox is now unchecked
            eventmanager.fire_checkbox_unchecked_event(self, self.scene.name)


class RelationshipAnnotation(Annotation):
    def __init__(self):
        super().__init__()
        self.text = ""
        self.to_object: PhysicalObject = None


class FeedbackAnnotation(Annotation):

    def __init__(self):
        super().__init__()

        self.show_inactive = BooleanAnnotationProperty("Show Inactive", True, self, self.set_show_inactive.__name__)
        self.properties.append(self.show_inactive)

        self.show_good = BooleanAnnotationProperty("Show Good", False, self, self.set_show_good.__name__)
        self.properties.append(self.show_good)

        self.show_average = BooleanAnnotationProperty("Show Average", False, self, self.set_show_average.__name__)
        self.properties.append(self.show_average)

        self.show_bad = BooleanAnnotationProperty("Show Bad", False, self, self.set_show_bad.__name__)
        self.properties.append(self.show_bad)

        self.radius = IntAnnotationProperty("Radius", 50, self)
        self.properties.append(self.radius)

        self.text_thickness = IntAnnotationProperty("Text Thickness", 1, self)
        self.properties.append(self.text_thickness)

        self.font_scale = FloatAnnotationProperty("Font Scale", .75, self)
        self.properties.append(self.font_scale)

        self.text_color = ColorAnnotationProperty("Text Color", (0, 0, 0), self)
        self.properties.append(self.text_color)

    def set_show_inactive(self, value):
        self.show_inactive._value = value
        if value:
            self.show_good._value = False
            self.show_average._value = False
            self.show_bad._value = False
        else:
            self.show_good._value = True
            self.show_average._value = False
            self.show_bad._value = False
        return True

    def set_show_good(self, value):
        self.show_good._value = value
        if value:
            self.show_average._value = False
            self.show_bad._value = False
            self.show_inactive._value = False
        else:
            self.show_average._value = False
            self.show_bad._value = False
            self.show_inactive._value = True
        return True

    def set_show_average(self, value):
        self.show_average._value = value
        if value:
            self.show_good._value = False
            self.show_bad._value = False
            self.show_inactive._value = False
        else:
            self.show_good._value = False
            self.show_bad._value = False
            self.show_inactive._value = True
        return True

    def set_show_bad(self, value):
        self.show_bad._value = value
        if value:
            self.show_good._value = False
            self.show_average._value = False
            self.show_inactive._value = False
        else:
            self.show_good._value = False
            self.show_average._value = False
            self.show_inactive._value = True
        return True

    def reset_runtime_state(self):
        self.set_show_inactive(True)


class CounterAnnotation(Annotation):

    def __init__(self):
        super().__init__()

        self.target_number = IntAnnotationProperty("Target number", 50, self)
        self.properties.append(self.target_number)

        self.text = StringAnnotationProperty("Text", AudioAnnotation.DEFAULT_TEXT, self)
        self.properties.append(self.text)

        self.text_thickness = IntAnnotationProperty("Text Thickness", 1, self)
        self.properties.append(self.text_thickness)

        self.font_scale = FloatAnnotationProperty("Font Scale", .5, self)
        self.properties.append(self.font_scale)

        self.text_color = ColorAnnotationProperty("Text Color", (0, 0, 0), self)
        self.properties.append(self.text_color)

        self.current_number = 0

    def increment(self):
        if self.current_number < self.target_number:
            self.current_number = self.current_number + 1

    def decrement(self):
        if self.current_number > 0:
            self.current_number = self.current_number - 1

    def reset(self):
        self.current_number = 0

    def reset_runtime_state(self):
        self.current_number = 0


annotation_counters = {
    LineAnnotation.__name__: 0,
    RectangleAnnotation.__name__: 0,
    CircleAnnotation.__name__: 0,
    TimerAnnotation.__name__: 0,
    VideoAnnotation.__name__: 0,
    AudioAnnotation.__name__: 0,
    ImageAnnotation.__name__: 0,
    TextAnnotation.__name__: 0,
    ArrowAnnotation.__name__: 0,
    RelationshipAnnotation.__name__: 0,
    CheckboxAnnotation.__name__: 0,
    ActionButtonAnnotation.__name__: 0,
    CurveAnnotation.__name__: 0,
    AnimationAnnotation.__name__: 0,
    FeedbackAnnotation.__name__: 0,
    ObjectAreaAnnotation.__name__: 0,
    CounterAnnotation.__name__: 0

}


# ==========================================================
# =========== Annotation Properties ========================
# ==========================================================

class AnnotationPropertiesModel(QAbstractTableModel):
    def __init__(self):
        super().__init__()
        self.__annotation = None
        self.__properties = None

    def set_annotation(self, annotation):
        self.__annotation = annotation
        if self.__annotation is None:
            self.__properties = None
        else:
            self.__properties = annotation.properties

        self.endResetModel()

    def rowCount(self, n):
        if self.__properties is None:
            return 0

        return len(self.__properties)

    def columnCount(self, n):
        return 2

    def data(self, index, role):
        if self.__properties is None:
            return

        if role == Qt.DisplayRole:
            prop: AnnotationProperty = self.__properties[index.row()]
            column = index.column()
            if column == 0:
                return prop.name
            elif column == 1:
                return prop.get_str_value()

    def setData(self, index, value, role):
        if self.__properties is None:
            return

        result = False
        if role == Qt.EditRole:
            prop = None
            try:
                prop: AnnotationProperty = self.__properties[index.row()]
                result = prop.set_value(value)
            except Exception as exp:
                logger.error("Could not set property value {}".format(prop))
                logger.error(exp)
                traceback.print_tb(exp.__traceback__)
                return False

        self.dataChanged.emit(index, index)
        return result

    def get_annotation_property(self, index):
        if self.__properties is None:
            return

        return self.__properties[index.row()]

    def flags(self, index):
        if index.column() == 1:
            return Qt.ItemIsEditable | super().flags(index)
        return super().flags(index)

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return ["Name", "Value"][section]


class AnnotationPropertyItemDelegate(QStyledItemDelegate):
    def __init__(self):
        super().__init__()
        self.phys_obj_model = None
        self.phys_obj_combo_items = []
        self.actions_combo_items = []

        self.filename = None
        self.editor = None

    def createEditor(self, parent, option, index: QModelIndex):
        if not self.phys_obj_model:
            return super().createEditor(parent, option, index)

        if index.column() != 1:
            return

        annotation_property = index.model().get_annotation_property(index)
        if isinstance(annotation_property, PhysicalObjectAnnotationProperty):
            combo = QComboBox(parent)
            self.phys_obj_combo_items.clear()
            self.phys_obj_combo_items.append(None)
            self.phys_obj_combo_items.extend(self.phys_obj_model.get_scene_physical_objects())
            combo.clear()
            for phys_obj in self.phys_obj_combo_items:
                if phys_obj is not None:
                    combo.addItem(phys_obj.name)
                else:
                    combo.addItem("None")

            if annotation_property.get_value() is None:
                combo.setCurrentIndex(0)
            else:
                index = -1
                for phys_obj in self.phys_obj_combo_items:
                    index += 1
                    if phys_obj is not None and phys_obj.name == annotation_property.get_value().name:
                        combo.setCurrentIndex(index)

            combo.currentIndexChanged.connect(self.physical_object_combo_index_changed)
            self.editor = combo
            return combo

        elif isinstance(annotation_property, FilePathAnnotationProperty):
            file_path_editor = FilePathEditorWidget(parent)
            file_path_editor.filename_selected.connect(self.file_dialog_file_selected)
            self.editor = file_path_editor
            return file_path_editor

        elif isinstance(annotation_property, BooleanAnnotationProperty):
            boolean_combo = QComboBox(parent)
            boolean_combo.clear()
            boolean_combo.addItem("True")
            boolean_combo.addItem("False")
            if annotation_property.get_value() is True:
                boolean_combo.setCurrentIndex(0)
            else:
                boolean_combo.setCurrentIndex(1)
            boolean_combo.currentIndexChanged.connect(self.boolean_combo_index_changed)
            self.editor = boolean_combo
            return boolean_combo

        elif isinstance(annotation_property, ActionAnnotationProperty):
            from isar.services import servicemanager
            from isar.services.servicemanager import ServiceNames
            action_service = servicemanager.get_service(ServiceNames.ACTIONS_SERVICE)
            self.actions_combo_items = []
            self.actions_combo_items.append(None)
            self.actions_combo_items.extend(action_service.get_available_actions())

            combo = QComboBox(parent)
            combo.clear()
            for action in self.actions_combo_items:
                if action is not None:
                    combo.addItem(action.name)
                else:
                    combo.addItem("None")

            if annotation_property.get_value() is None:
                combo.setCurrentIndex(0)
            else:
                index = -1
                for action in self.actions_combo_items:
                    index += 1
                    if action is not None and action.name == annotation_property.get_value().name:
                        combo.setCurrentIndex(index)

            combo.currentIndexChanged.connect(self.on_select_actions_combo_index_changed)
            self.editor = combo
            return combo
        else:
            self.editor = super().createEditor(parent, option, index)
            return self.editor

    def setModelData(self, editor, model, index):
        if isinstance(editor, QComboBox):
            annotation_property = index.model().get_annotation_property(index)
            combo_index = editor.currentIndex()
            if combo_index == -1:
                return
            if isinstance(annotation_property, PhysicalObjectAnnotationProperty):
                phys_obj = self.phys_obj_combo_items[combo_index]
                model.setData(index, phys_obj, Qt.EditRole)
            elif isinstance(annotation_property, BooleanAnnotationProperty):
                if combo_index == 0:
                    model.setData(index, True, Qt.EditRole)
                elif combo_index == 1:
                    model.setData(index, False, Qt.EditRole)
            elif isinstance(annotation_property, ActionAnnotationProperty):
                action = self.actions_combo_items[combo_index]
                model.setData(index, action, Qt.EditRole)

        elif isinstance(editor, FilePathEditorWidget):
            annotation_property = index.model().get_annotation_property(index)
            if isinstance(annotation_property, FilePathAnnotationProperty):
                model.setData(index, self.filename, Qt.EditRole)

        else:
            super().setModelData(editor, model, index)

    def physical_object_combo_index_changed(self):
        self.commitData.emit(self.sender())

    def file_dialog_file_selected(self, filename):
        self.filename = filename
        self.commitData.emit(self.sender())

    def boolean_combo_index_changed(self):
        self.commitData.emit(self.sender())

    def on_select_actions_combo_index_changed(self):
        self.commitData.emit(self.sender())


class FilePathEditorWidget(QWidget):
    filename_selected = pyqtSignal(str)

    def __init__(self, parent):
        super().__init__(parent)

        self.filename = None

        self.widget = QWidget(self)
        self.widget.setAutoFillBackground(True)
        # widget.setMinimumHeight(80)
        # widget.setMinimumWidth(100)
        self.label = QLabel()
        self.label.setSizePolicy(QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding))

        self.button = QPushButton("...")
        self.label.setSizePolicy(QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding))
        self.button.clicked.connect(self.btn_clicked)

        hbox = QHBoxLayout(self.widget)
        hbox.setContentsMargins(0, 0, 0, 0)
        hbox.setSpacing(3)
        hbox.addWidget(self.label)
        hbox.addWidget(self.button)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(2, 2, 2, 2)
        self.layout.addWidget(self.widget)

    def btn_clicked(self):
        self.filename, _ = QFileDialog.getOpenFileName()
        if self.filename is not None:
            self.filename_selected.emit(self.filename)


class AnnotationProperty:
    def __init__(self, name, value, annotation, setter_name=None):
        self.name = name
        self._value = value
        self.annotation = annotation
        # we use the callback name for setter instead of directly the callable object,
        # becuause of jsonpickle serialization.
        self.setter_name = setter_name

    def get_str_value(self):
        return str(self._value)

    def set_value(self, value):
        # It is important that the annotation property sets its value.
        raise TypeError("Must be implemented by subclasses")

    def get_value(self):
        return self._value


class ColorAnnotationProperty(AnnotationProperty):
    def __init__(self, name, value, annotation):
        super().__init__(name, value, annotation)

    def set_value(self, value):
        if isinstance(value, str):
            literal, success = sceneutil.get_color_from_str(value)
            if literal and success:
                if self.setter_name is not None:
                    return getattr(self.annotation, self.setter_name)(literal)
                else:
                    self._value = literal
                    return True
            else:
                return False
        else:
            if isinstance(value, tuple) and \
                    len(value) == 2 and \
                    isinstance(value[0], int) and \
                    isinstance(value[1], int) and \
                    isinstance(value[2], int):
                if self.setter_name is not None:
                    return getattr(self.annotation, self.setter_name)(value)
                else:
                    self._value = value
                    return True
            else:
                return False


class FilePathAnnotationProperty(AnnotationProperty):
    def set_value(self, value):
        # copy the file to the project's basedir
        # set the _value to only the file name
        if os.path.exists(value):
            shutil.copy(value, scenemodel.current_project.base_path)
            value = os.path.basename(value)
            if self.setter_name is not None:
                return getattr(self.annotation, self.setter_name)(value)
            else:
                self._value = value
                return True
        else:
            return False


class PhysicalObjectAnnotationProperty(AnnotationProperty):
    def get_str_value(self):
        if self._value is None:
            return "None"
        else:
            return self._value.name

    def set_value(self, phys_obj):
        if self.setter_name is not None:
            return getattr(self.annotation, self.setter_name)(phys_obj)
        else:
            return False


class IntTupleAnnotationProperty(AnnotationProperty):
    def set_value(self, value):
        if isinstance(value, str):
            literal = sceneutil.get_literal_from_str(value)
            if literal and \
                    isinstance(literal, tuple) and \
                    len(literal) == 2 and \
                    isinstance(literal[0], int) and \
                    isinstance(literal[1], int):
                if self.setter_name is not None:
                    return getattr(self.annotation, self.setter_name)(literal)
                else:
                    self._value = literal
                    return True
            else:
                return False
        else:
            if isinstance(value, tuple) and \
                    len(value) == 2 and \
                    isinstance(value[0], int) and \
                    isinstance(value[1], int):
                if self.setter_name is not None:
                    return getattr(self.annotation, self.setter_name)(value)
                else:
                    self._value = value
                    return True
            else:
                return False


class FloatAnnotationProperty(AnnotationProperty):
    def set_value(self, value):
        if isinstance(value, str):
            literal = sceneutil.get_literal_from_str(value)
            if literal and isinstance(literal, (float, int)):
                if self.setter_name is not None:
                    return getattr(self.annotation, self.setter_name)(literal)
                else:
                    self._value = literal
                    return True
            else:
                return False
        else:
            if isinstance(value, (float, int)):
                if self.setter_name is not None:
                    return getattr(self.annotation, self.setter_name)(value)
                else:
                    self._value = value
                    return True
            else:
                return False


class IntAnnotationProperty(AnnotationProperty):
    def set_value(self, value):
        if isinstance(value, str):
            literal = sceneutil.get_literal_from_str(value)
            if literal and isinstance(literal, int):
                if self.setter_name is not None:
                    return getattr(self.annotation, self.setter_name)(literal)
                else:
                    self._value = literal
                    return True
            else:
                return False
        else:
            if isinstance(value, int):
                if self.setter_name is not None:
                    return getattr(self.annotation, self.setter_name)(value)
                else:
                    self._value = value
                    return True
            else:
                return False


class StringAnnotationProperty(AnnotationProperty):
    def set_value(self, value):
        self._value = value
        return True


class BooleanAnnotationProperty(AnnotationProperty):
    def set_value(self, value):
        if isinstance(value, str):
            literal = sceneutil.get_literal_from_str(value)
            if literal is not None and isinstance(literal, bool):
                if self.setter_name is not None:
                    return getattr(self.annotation, self.setter_name)(literal)
                else:
                    self._value = literal
                    return True
            else:
                return False
        else:
            if isinstance(value, bool):
                if self.setter_name is not None:
                    return getattr(self.annotation, self.setter_name)(value)
                else:
                    self._value = value
                    return True
            else:
                return False


class ActionAnnotationProperty(AnnotationProperty):
    def get_str_value(self):
        if self._value is None:
            return "None"
        else:
            return self._value.name

    def set_value(self, value):
        self._value = value
        return True
