import logging
import math
from ast import literal_eval
from typing import List

from PyQt5 import QtCore
from PyQt5.QtCore import QAbstractListModel, Qt, QModelIndex, QAbstractTableModel
from PyQt5.QtWidgets import QCheckBox, QComboBox, QItemDelegate

from isar.scene import util
from isar.scene.physicalobjectmodel import PhysicalObject
from isar.scene.scenemodel import Scene

logger = logging.getLogger("isar.annotationmodel")


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
            new_name = self.__annotations[index.row()].name
            try:
                if util.is_valid_name(str(value)):
                    new_name = str(value)
            except Exception as e:
                print("Error editing annotation name", e)
                return False

            self.__annotations[index.row()].name = new_name
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

        new_annotation.scene = self.__scene
        self.__scene.add_annotation(new_annotation)
        self.__annotations = self.__scene.get_all_annotations()

        annotation_counters[class_name] += 1
        self.current_annotation = new_annotation
        self.endInsertRows()

    def delete_annotation(self, selected_index):
        # TODO: remove properly using remove rows (see insert rows)
        if self.__scene is None:
            return

        if len(self.__annotations) == 0:    # keep at least one scene
            return

        if len(self.__annotations) <= selected_index.row():
            return

        annotation = self.__annotations[selected_index.row()]
        annotation.scene = None
        self.__scene.remove_annotation(annotation)
        self.__annotations = self.__scene.get_all_annotations()

        self.removeRow(selected_index.row())
        self.update_view(selected_index)

    def update_view(self, index):
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

    def get_all_annotations(self):
        if self.__annotations:
            return tuple(self.__annotations)
        else:
            return ()

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
        self.scene = None
        # Owner of  an annotation is either the scene or a physical object. An annotation can have only one owner.
        self.owner = None
        self.properties: List[AnnotationProperty] = []

        self.position = IntTupleAnnotationProperty("Position", (0, 0), self, self.set_position)
        self.properties.append(self.position)

        self.attached_to = PhysicalObjectAnnotationProperty("Attach To", None, self, self.set_attached_to)
        self.properties.append(self.attached_to)

        self.update_orientation = BooleanAnnotationProperty("Update Orientation", False, self)
        self.properties.append(self.update_orientation)

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
            self.owner = self.scene
            self.scene.add_annotation(self)

            if old_phys_obj is not None:
                old_phys_obj.remove_annotation(self)

            self.set_position((0, 0))
            return True

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


class TextAnnotation(Annotation):
    DEFAULT_TEXT = "Set the text in annotation properties view."

    def __init__(self):
        super().__init__()
        self.text = StringAnnotationProperty("Text", TextAnnotation.DEFAULT_TEXT, self)
        self.properties.append(self.text)

        self.color = ColorAnnotationProperty("Color", (0, 255, 0), self)
        self.properties.append(self.color)

        self.thickness = IntAnnotationProperty("Thickness", 3, self)
        self.properties.append(self.thickness)

        self.font_scale = IntAnnotationProperty("Font Scale", 2, self)
        self.properties.append(self.font_scale)


class ArrowAnnotation(Annotation):
    def __init__(self):
        super().__init__()
        self.text = ""
        self.start = [0.0, 0.0]
        self.end = [0.0, 0.0]
        self.thickness = 3


class SelectBoxAnnotation(Annotation):
    def __init__(self):
        super().__init__()
        self.text = ""


class LineAnnotation(Annotation):

    MINIMUM_LENGTH = 10

    def __init__(self):
        super().__init__()

        self.start = IntTupleAnnotationProperty("Start", [0, 0], self, self.set_start)
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

        self.center = IntTupleAnnotationProperty("Center", [0, 0], self, self.set_center)
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


class RelationshipAnnotation(Annotation):
    def __init__(self):
        super().__init__()
        self.text = ""
        self.to_object: PhysicalObject = None


class AudioAnnotation(Annotation):
    def __init__(self):
        super(AudioAnnotation, self).__init__()
        self.audio_path = ""


class VideoAnnotation(Annotation):
    def __init__(self):
        super(VideoAnnotation, self).__init__()
        self.video_path = ""


class ImageAnnotation(Annotation):
    def __init__(self):
        super(ImageAnnotation, self).__init__()
        self.image_path = ""
        self.width = 0
        self.height = 0


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
    SelectBoxAnnotation.__name__: 0
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
            except Exception as e:
                print("error", e)
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


class AnnotationPropertyItemDelegate(QItemDelegate):
    def __init__(self):
        super().__init__()
        self.phys_obj_model = None
        self.phys_obj_combo_items = []

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

            combo.currentIndexChanged.connect(self.current_index_changed)
            return combo

        elif isinstance(annotation_property, BooleanAnnotationProperty):
            # TODO: implement update_orientation
            pass

        else:
            return super().createEditor(parent, option, index)

    def setModelData(self, editor, model, index):
        if isinstance(editor, QComboBox):
            # TODO: find the property that requires a phys obj value and set its value
            annotation_property = index.model().get_annotation_property(index)
            if isinstance(annotation_property, PhysicalObjectAnnotationProperty):
                combo_index = editor.currentIndex()
                if combo_index == -1:
                    return
                phys_obj = self.phys_obj_combo_items[combo_index]
                model.setData(index, phys_obj, Qt.EditRole)

        elif isinstance(editor, QCheckBox):
            # TODO: implement
            pass

        else:
            super().setModelData(editor, model, index)

    def current_index_changed(self):
        self.commitData.emit(self.sender())


class AnnotationProperty:
    def __init__(self, name, value, annotation, setter=None):
        self.name = name
        self._value = value
        self.annotation = annotation
        self.setter = setter

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
                if self.setter is not None:
                    return self.setter(literal)
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
                if self.setter is not None:
                    return self.setter(value)
                else:
                    self._value = value
                    return True
            else:
                return False


class FilePathAnnotationProperty(AnnotationProperty):
    pass


class PhysicalObjectAnnotationProperty(AnnotationProperty):
    def get_str_value(self):
        if self._value is None:
            return "None"
        else:
            return self._value.name

    def set_value(self, phys_obj):
        if self.setter is not None:
            return self.setter(phys_obj)
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
                if self.setter is not None:
                    return self.setter(literal)
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
                if self.setter is not None:
                    return self.setter(value)
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
                if self.setter is not None:
                    return self.setter(literal)
                else:
                    self._value = literal
                    return True
            else:
                return False
        else:
            if isinstance(value, (float, int)):
                if self.setter is not None:
                    return self.setter(value)
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
                if self.setter is not None:
                    return self.setter(literal)
                else:
                    self._value = literal
                    return True
            else:
                return False
        else:
            if isinstance(value, int):
                if self.setter is not None:
                    return self.setter(value)
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
    pass





