from isar.scene.annotationmodel import Annotation, ColorAnnotationProperty, AnnotationProperty, IntAnnotationProperty, \
    FilePathAnnotationProperty, BooleanAnnotationProperty, get_literal_from_str


class CurveAnnotation(Annotation):

    def __init__(self):
        super(CurveAnnotation, self).__init__()

        self.color = ColorAnnotationProperty("Color", (0, 0, 0), self)
        self.properties.append(self.color)

        self.thickness = IntAnnotationProperty("Thickness", 3, self)
        self.properties.append(self.thickness)

        self.line_coordinates = ArrayTupleAnnotationProperty("Line Coordinates", None, self)
        self.properties.append(self.line_coordinates)

    def set_position(self, position):
        self.position._value = position
        self.center._value = position
        return True


class ObjectCurveAnnotation(Annotation):

    def __init__(self):
        super(ObjectCurveAnnotation, self).__init__()

        self.color = ColorAnnotationProperty("Color", (0, 0, 0), self)
        self.properties.append(self.color)

        self.thickness = IntAnnotationProperty("Thickness", 3, self)
        self.properties.append(self.thickness)

        self.line_coordinates = ArrayTupleAnnotationProperty("Line Coordinates", None, self)
        self.properties.append(self.line_coordinates)

        self.image_path = FilePathAnnotationProperty("ImageFilename", None, self)
        self.properties.append(self.image_path)

        self.width = IntAnnotationProperty("Width", 5, self)
        self.properties.append(self.width)

        self.height = IntAnnotationProperty("Height", 5, self)
        self.properties.append(self.height)

        self.keep_aspect_ratio = BooleanAnnotationProperty("Keep Aspect Ratio", True, self)
        self.properties.append(self.keep_aspect_ratio)

    def set_position(self, position):
        self.position._value = position
        self.center._value = position
        return True


class ArrayTupleAnnotationProperty(AnnotationProperty):

    def set_value(self, value):
        if isinstance(value, str):
            literal = get_literal_from_str(value)
            if literal and \
                    isinstance(literal, list) and \
                    isinstance(literal[0], tuple) and \
                    isinstance(literal[0][0], int) and \
                    isinstance(literal[0][1], int):
                if self.setter_name is not None:
                    return getattr(self.annotation, self.setter_name)(literal)
                else:
                    self._value = literal
                    return True
            else:
                return False
        else:
            if isinstance(value, list) and \
                    isinstance(value[0], tuple) and \
                    isinstance(value[0][0], int) and \
                    isinstance(value[0][1], int):
                if self.setter_name is not None:
                    return getattr(self.annotation, self.setter_name)(value)
                else:
                    self._value = value
                    return True
            else:
                return False
