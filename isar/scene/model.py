from PyQt5 import QtCore
from PyQt5.QtCore import QAbstractItemModel, QAbstractListModel, QModelIndex


class ScenesModel(QAbstractListModel):
    def __init__(self):
        super().__init__()
        self.scenes = []

    def rowCount(self, parent):
        return len(self.scenes)

    def data(self, index:QModelIndex, role):
        if role == QtCore.Qt.DisplayRole:
            return self.scenes[index.row()].name


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

