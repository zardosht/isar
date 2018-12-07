import logging

from PyQt5 import QtCore
from PyQt5.QtCore import QAbstractListModel, Qt, QModelIndex

from isar.scene import util
from isar.scene.physicalobjectmodel import PhysicalObject


logger = logging.getLogger("isar.annotationmodel")


class AnnotationsModel(QAbstractListModel):
    editCompleted = QtCore.pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.current_annotation = None
        self.__scene = None
        self.__annotations = None

    def set_scene(self, scene):
        self.__scene = scene
        self.__annotations = scene.get_annotations()

    def rowCount(self, parent):
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

        return True  # edit was done correctly

    def flags(self, index):
        return Qt.ItemIsSelectable | Qt.ItemIsEditable | Qt.ItemIsEnabled

    def add_annotation(self, new_annotation):
        if self.__annotations is None:
            return

        at_row = self.rowCount(None) + 1
        self.beginInsertRows(QModelIndex(), at_row, at_row)
        self.insertRow(at_row)
        class_name = new_annotation.__class__.__name__
        new_annotation.name = new_annotation.__class__.__name__ + str(annotation_counters[class_name])

        self.__annotations.append(new_annotation)

        annotation_counters[class_name] += 1
        self.current_annotation = new_annotation
        self.endInsertRows()

    def delete_annotation(self, selected_index):
        # TODO: remove properly using remove rows (see insert rows)
        if self.__annotations is None:
            return

        if len(self.__annotations) == 0:    # keep at least one scene
            return

        if len(self.__annotations) <= selected_index.row():
            return

        del self.__annotations[selected_index.row()]
        self.removeRow(selected_index.row())
        self.update_view(selected_index)

    def update_view(self, index):
        self.dataChanged.emit(index, index, [Qt.DisplayRole])

    def set_current_annotation(self, selected_index):
        if self.__annotations is None:
            return

        self.current_annotation = self.__annotations[selected_index.row()]

    def get_annotations(self):
        if self.__annotations:
            return tuple(self.__annotations)
        else:
            return ()


class Annotation:
    def __init__(self):
        self.position = [0.0, 0.0]
        self.attached_to: PhysicalObject = None
        self.updateOrientation = False


# class AnnotationPropertyItem:
#     def __init__(self):


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
    def __init__(self):
        super().__init__()
        self.start = [0.0, 0.0]
        self.end = None
        self.thikness = 3
        self.color = (0, 255, 255)


class RectangleAnnotation(Annotation):
    def __init__(self):
        super(RectangleAnnotation, self).__init__()
        self.color = (255, 0, 255)
        self.thikness = 3
        self.vertex1 = [0.0, 0.0]
        self.vertex2 = None


class CircleAnnotation(Annotation):
    def __init__(self):
        super(CircleAnnotation, self).__init__()
        self.center = [0.0, 0.0]
        self.color = (125, 125, 255)
        self.radius = None
        self.thikness = 3


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

