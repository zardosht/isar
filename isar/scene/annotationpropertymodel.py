import logging
from ast import literal_eval
from PyQt5.QtCore import QAbstractTableModel, Qt


logger = logging.getLogger("isar.annotationpropertymodel")


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

    def flags(self, index):
        if index.column() == 1:
            return Qt.ItemIsEditable | super().flags(index)
        return super().flags(index)

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return ["Name", "Value"][section]


def get_literal_from_str(str_val):
    value = None
    if isinstance(str_val, str):
        try:
            value = literal_eval(str_val)
        except Exception as e:
            logger.error("Error converting value:", e)
        finally:
            return value


class AnnotationProperty:
    def __init__(self, name, value):
        self.name = name
        self._value = value

    def get_str_value(self):
        return str(self._value)

    def set_value(self, value):
        raise TypeError("Must be implemented by subclasses")

    def get_value(self):
        return self._value


class ColorAnnotationProperty(AnnotationProperty):
    def __init__(self, name, value):
        super().__init__(name, value)

    def set_value(self, value):
        if isinstance(value, str):
            literal = get_literal_from_str(value)
            if literal and \
                    isinstance(literal, tuple) and \
                    len(literal) == 3 and \
                    isinstance(literal[0], int) and \
                    isinstance(literal[1], int) and \
                    isinstance(literal[2], int):
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
                self._value = value
                return True
            else:
                return False


class FilePathAnnotationProperty(AnnotationProperty):
    def __init__(self, name, value):
        super().__init__(name, value)


class PhysicalObjectAnnotationProperty(AnnotationProperty):
    def __init__(self, name, value):
        super().__init__(name, value)


class RelativeLengthAnnotationProperty(AnnotationProperty):
    def get_str_value(self):
        return "{:.2f}".format(self._value * 100)

    def set_value(self, value):
        if isinstance(value, str):
            literal = get_literal_from_str(value)
            if literal:
                self._value = literal / 100
                return True
            else:
                return False
        else:
            if isinstance(value, (float, int)):
                self._value = float(value)
                return True
            else:
                return False


class RelativePositionAnnotationProperty(AnnotationProperty):
    def get_str_value(self):
        return "({})".format(", ".join("{:.2f}".format(x * 100) for x in self._value))

    def set_value(self, value):
        if isinstance(value, str):
            literal = get_literal_from_str(value)
            if literal and isinstance(literal, tuple) and len(literal) == 2:
                    self._value = tuple(x / 100 for x in literal)
                    return True
            else:
                return False
        else:
            if isinstance(value, tuple) and len(value) == 2:
                self._value = tuple(float(x) for x in value)
                return True
            else:
                return False


class FloatTupleAnnotationProperty(AnnotationProperty):
    def __init__(self, name, value):
        super().__init__(name, value)

    def set_value(self, value):
        if isinstance(value, str):
            literal = get_literal_from_str(value)
            if literal and isinstance(literal, tuple) and len(literal) == 2:
                    self._value = tuple(float(x) for x in literal)
                    return True
            else:
                return False
        else:
            if isinstance(value, tuple) and len(value) == 2:
                self._value = tuple(float(x) for x in value)
                return True
            else:
                return False


class IntTupleAnnotationProperty(AnnotationProperty):
    def __init__(self, name, value):
        super().__init__(name, value)

    def set_value(self, value):
        if isinstance(value, str):
            literal = get_literal_from_str(value)
            if literal and \
                    isinstance(literal, tuple) and \
                    len(literal) == 2 and \
                    isinstance(literal[0], int) and \
                    isinstance(literal[1], int):
                self._value = literal
                return True
            else:
                return False
        else:
            if isinstance(value, tuple) and \
                    len(value) == 2 and \
                    isinstance(value[0], int) and \
                    isinstance(value[1], int):
                self._value = value
                return True
            else:
                return False


class FloatAnnotationProperty(AnnotationProperty):
    def __init__(self, name, value):
        super().__init__(name, value)

    def set_value(self, value):
        if isinstance(value, str):
            literal = get_literal_from_str(value)
            if literal and isinstance(literal, (float, int)):
                self._value = float(literal)
                return True
            else:
                return False
        else:
            if isinstance(value, (float, int)):
                self._value = value
                return True
            else:
                return False


class IntAnnotationProperty(AnnotationProperty):
    def __init__(self, name, value):
        super().__init__(name, value)

    def set_value(self, value):
        if isinstance(value, str):
            literal = get_literal_from_str(value)
            if literal and isinstance(literal, int):
                self._value = literal
                return True
            else:
                return False
        else:
            if isinstance(value, int):
                self._value = value
                return True
            else:
                return False


class BooleanAnnotationProperty(AnnotationProperty):
    def __init__(self, name, value):
        super().__init__(name, value)


class StringAnnotationProperty(AnnotationProperty):
    def __init__(self, name, value):
        super().__init__(name, value)

