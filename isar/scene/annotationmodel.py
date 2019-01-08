import logging
from typing import List

from PyQt5 import QtCore
from PyQt5.QtCore import QAbstractListModel, Qt, QModelIndex

from isar.scene import util
from isar.scene.annotationpropertymodel import FloatTupleAnnotationProperty, IntAnnotationProperty, \
    ColorAnnotationProperty, FloatAnnotationProperty, PhysicalObjectAnnotationProperty, AnnotationProperty, \
    BooleanAnnotationProperty, RelativePositionAnnotationProperty, RelativeLengthAnnotationProperty, \
    IntTupleAnnotationProperty
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

        self.position = IntTupleAnnotationProperty("Position", (0, 0), self)

        self.attached_to = PhysicalObjectAnnotationProperty("Attach To", None, self)
        self.properties.append(self.attached_to)

        self.update_orientation = BooleanAnnotationProperty("Update Orientation", False, self)
        self.properties.append(self.update_orientation)


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
    def __init__(self):
        super().__init__()
        self.text = ""


class ArrowAnnotation(Annotation):
    def __init__(self):
        super().__init__()
        self.text = ""
        self.start = [0.0, 0.0]
        self.end = [0.0, 0.0]
        self.thikness = 3


class SelectBoxAnnotation(Annotation):
    def __init__(self):
        super().__init__()
        self.text = ""


class LineAnnotation(Annotation):

    MINIMUM_LENGTH = 0.001

    def __init__(self):
        super().__init__()

        self.start = IntTupleAnnotationProperty("Start", [0, 0], self)
        self.properties.append(self.start)

        self.end = IntTupleAnnotationProperty("End", None, self)
        self.properties.append(self.end)

        self.thikness = IntAnnotationProperty("Thikness", 3, self)
        self.properties.append(self.thikness)

        self.color = ColorAnnotationProperty("Color", (0, 255, 255), self)
        self.properties.append(self.color)


class RectangleAnnotation(Annotation):

    MINIMUM_AREA = 0.00001

    def __init__(self):
        super(RectangleAnnotation, self).__init__()

        self.color = ColorAnnotationProperty("Color", (255, 0, 255), self)
        self.properties.append(self.color)

        self.thikness = IntAnnotationProperty("Thikness", 3, self)
        self.properties.append(self.thikness)

        self.vertex1 = IntTupleAnnotationProperty("Vertex1", [0, 0], self)
        self.properties.append(self.vertex1)

        self.vertex2 = IntTupleAnnotationProperty("Vertex2", None, self)
        self.properties.append(self.vertex2)


class CircleAnnotation(Annotation):

    MINIMUM_RADIUS = 0.001

    def __init__(self):
        super(CircleAnnotation, self).__init__()

        self.color = ColorAnnotationProperty("Color", (125, 125, 255), self)
        self.properties.append(self.color)

        self.center = IntTupleAnnotationProperty("Center", [0, 0], self)
        self.properties.append(self.center)

        self.radius = IntAnnotationProperty("Radius", None, self)
        self.properties.append(self.radius)

        self.thikness = IntAnnotationProperty("Thikness", 3, self)
        self.properties.append(self.thikness)


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

