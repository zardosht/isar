import logging
import os
import shutil
import traceback
from ast import literal_eval
from typing import List

from PyQt5 import QtCore
from PyQt5.QtCore import QAbstractListModel, Qt, QModelIndex, QAbstractTableModel, pyqtSignal, QSize
from PyQt5.QtWidgets import QComboBox, QFileDialog, QStyledItemDelegate, QWidget, QHBoxLayout, \
    QPushButton, QLabel, QToolButton, QVBoxLayout, QSizePolicy

from isar.events import actionsservice
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
        self.endResetModel()

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

    def set_position(self, position):
        self.position._value = position
        self.center._value = position
        return True

    def set_center(self, center):
        self.center._value = center
        self.position._value = center
        return True


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

    def intersects_with_point(self, point):
        position = self.position.get_value()
        width = self.width.get_value()
        height = self.height.get_value()
        return position[0] <= point[0] <= position[0] + width and \
               position[1] <= point[1] <= position[1] + height


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
        #  Generally, the bahavior of annotations upon selection, should be defined
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

    def intersects_with_point(self, point):
        position = self.position.get_value()
        if position is None:
            return False

        width = self.width.get_value()
        height = self.height.get_value()
        return (position[0] - int(width / 2)) <= point[0] <= (position[0] + int(width / 2)) and \
               (position[1] - int(height / 2)) <= point[1] <= (position[1] + int(height / 2))

    def on_select(self):
        logger.info("Action Button Selected -------------------------------<><><><><><><<<<<<<<<")


class CurveAnnotation(Annotation):
    MINIMUM_NUMBER_POSITIONS = 5

    def __init__(self):
        super(CurveAnnotation, self).__init__()

        self.start = IntTupleAnnotationProperty("Start", [0, 0], self)
        self.properties.append(self.start)

        self.end = IntTupleAnnotationProperty("End", None, self)
        self.properties.append(self.end)

        self.color = ColorAnnotationProperty("Color", (0, 0, 0), self)
        self.properties.append(self.color)

        self.thickness = IntAnnotationProperty("Thickness", 2, self)
        self.properties.append(self.thickness)

        self.line_positions = []
        self.drawing_finished = False


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

        self.image_width = IntAnnotationProperty("Image Width", 20, self)
        self.properties.append(self.image_width)

        self.image_height = IntAnnotationProperty("Image Height", 20, self)
        self.properties.append(self.image_height)

        self.animation_speed = IntAnnotationProperty("Animation Speed", 2, self)
        self.properties.append(self.animation_speed)

        self.loop = BooleanAnnotationProperty("Loop", False, self)
        self.properties.append(self.loop)

        self.closed_curve = BooleanAnnotationProperty("Closed Curve", False, self)
        self.properties.append(self.closed_curve)

        self.line_positions = []
        self.mouse_released = False

    def intersects_with_point(self, point):
        position = self.line_start
        width = self.image_width.get_value()
        height = self.image_height.get_value()
        return position[0] <= point[0] <= position[0] + width and \
               position[1] <= point[1] <= position[1] + height


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


class RelationshipAnnotation(Annotation):
    def __init__(self):
        super().__init__()
        self.text = ""
        self.to_object: PhysicalObject = None


class SelectBoxAnnotation(Annotation):
    def __init__(self):
        super().__init__()
        self.text = ""


class TimerAnnotation(Annotation):
    def __init__(self):
        super(TimerAnnotation, self).__init__()
        self.duration = 10


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
    SelectBoxAnnotation.__name__: 0,
    ActionButtonAnnotation.__name__: 0,
    CurveAnnotation.__name__: 0,
    AnimationAnnotation.__name__: 0

}


# ==========================================================
# =========== Annotation Properties ========================
# ==========================================================


def get_literal_from_str(str_val):
    value = None
    if isinstance(str_val, str):
        if str_val == "":
            return value

        try:
            value = literal_eval(str_val)
        except Exception as e:
            logger.error("Error converting value:", e)
        finally:
            return value


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
            self.actions_combo_items = []
            self.actions_combo_items.extend(actionsservice.defined_actions)
            self.actions_combo_items.append(None)

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
            literal = get_literal_from_str(value)
            if literal and \
                    isinstance(literal, tuple) and \
                    len(literal) == 3 and \
                    isinstance(literal[0], int) and \
                    isinstance(literal[1], int) and \
                    isinstance(literal[2], int):
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
            literal = get_literal_from_str(value)
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
            literal = get_literal_from_str(value)
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
            literal = get_literal_from_str(value)
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
            literal = get_literal_from_str(value)
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
