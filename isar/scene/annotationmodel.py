from isar.scene.physicalobjectmodel import PhysicalObject


class Annotation:
    def __init__(self):
        self.type = ""
        self.position = [0.0, 0.0]
        self.attached_to: PhysicalObject = None
        self.updateOrientation = False


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
        super().__init__()
        self.text = ""


class ArrowAnnotation(Annotation):
    def __init__(self):
        super().__init__()
        self.text = ""
        self.start = [0.0, 0.0]
        self.end = [0.0, 0.0]
        self.thikness = 1


class SelectButtonAnnotation(Annotation):
    def __init__(self):
        super().__init__()
        self.text = ""


class LineAnnotation(Annotation):
    def __init__(self):
        super().__init__()
        self.start = [0.0, 0.0]
        self.end = [0.0, 0.0]
        self.thikness = 1


class RectangleAnnotation(Annotation):
    def __init__(self):
        super(RectangleAnnotation, self).__init__()
        self.color = ""
        self.thikness = 0
        self.width = 0
        self.height = 0


class CircleAnnotation(Annotation):
    def __init__(self):
        super(CircleAnnotation, self).__init__()
        self.color = ""
        self.radius = 0
        self.thikness = 0


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

