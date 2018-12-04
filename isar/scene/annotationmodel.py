import logging

from isar.scene.physicalobjectmodel import PhysicalObject


logger = logging.getLogger("isar.annotationmodel")

class Annotation:
    def __init__(self):
        self.position = [0.0, 0.0]
        self.attached_to: PhysicalObject = None
        self.updateOrientation = False


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

