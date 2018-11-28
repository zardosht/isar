import copy

from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QAbstractListModel


class ScenesModel(QAbstractListModel):
    editCompleted = QtCore.pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.scenes = []

    def rowCount(self, parent):
        return len(self.scenes)

    def data(self, index, role):
        if role == QtCore.Qt.DisplayRole:
            return self.scenes[index.row()].name

    def setData(self, index, value, role):
        if role == Qt.EditRole:
            new_name = self.scenes[index.row()].name
            try:
                if ScenesModel.is_valid_scene_name(str(value)):
                    new_name = str(value)
            except Exception as e:
                print("Error editing scene name", e)
                return False

            self.scenes[index.row()].name = new_name
            self.editCompleted.emit(new_name)

        return True  # edit was done correctly

    @staticmethod
    def is_valid_scene_name(name):
        if len(name)==0: return False
        is_valid = False
        is_valid = all(c.isalnum() or
                       c.isspace() or
                       c == "-" or
                       c == "_"
                       for c in name)
        return is_valid

    def flags(self, index):
        # answer to requests for cell flags from QTableView
        return Qt.ItemIsSelectable | Qt.ItemIsEditable | Qt.ItemIsEnabled

    def new_scene(self, at_index):
        self.insertRow(at_index.row())
        new_scene = Scene("New Scene")
        self.scenes.append(new_scene)
        self.update_view(at_index)

    def clone_scene(self, selected_index):
        if len(self.scenes) <= selected_index.row():
            return

        selected_scene = self.scenes[selected_index.row()]
        cloned_scene = copy.deepcopy(selected_scene)
        cloned_scene.name = "Cloned - " + selected_scene.name
        self.scenes.append(cloned_scene)
        self.update_view(selected_index)

    def delete_scene(self, selected_index):
        if len(self.scenes) == 1:    # keep at least one scene
            return

        if len(self.scenes) <= selected_index.row():
            return

        del self.scenes[selected_index.row()]
        self.removeRow(selected_index.row())

        self.update_view(selected_index)

    def update_view(self, index):
        self.dataChanged.emit(index, index, [Qt.DisplayRole])


class Scene:
    def __init__(self, name):
        self.name = name
        self.physical_objects = []
        self.annotation = []


class PhysicalObject:
    def __init__(self):
        self.name = ""
        self.image_path = ""
        self.image = None
        self.annotations = []


class Annotation:
    def __init__(self):
        self.type = ""
        self.position = [0.0, 0.0]
        self.text = ""
        self.start = [0.0, 0.0]
        self.end = [0.0, 0.0]
        self.video_path = ""
        self.audio_path = ""
        self.image_path = ""
        self.color = ""
        self.radius = 0
        self.thikness = 0
        self.width = 0
        self.height = 0
        self.updateOrientation = False


class AnnotationProperty:
    def __init__(self):
        pass


class AnnotationTool:
    def __init__(self):
        pass



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
        pass


class ArrowAnnotation(Annotation):
    def __init__(self):
        pass


class SelectButtonAnnotation(Annotation):
    def __init__(self):
        pass


class LineAnnotation(Annotation):
    def __init__(self):
        pass


class RectangleAnnotation(Annotation):
    def __init__(self):
        pass


class CircleAnnotation(Annotation):
    def __init__(self):
        pass


class RelationshipAnnotation(Annotation):
    def __init__(self):
        pass


class AudioAnnotation(Annotation):
    def __init__(self):
        pass


class VideoAnnotation(Annotation):
    def __init__(self):
        pass


class ImageAnnotation(Annotation):
    def __init__(self):
        pass


class TimerAnnotation(Annotation):
    def __init__(self):
        pass


dummy_scene_model = None


def create_dummy_scenes_model():
    global dummy_scene_model
    scene1 = Scene("scene1")
    dummy_scene_model = ScenesModel()
    dummy_scene_model.scenes.append(scene1)
    return dummy_scene_model

