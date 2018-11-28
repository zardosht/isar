

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