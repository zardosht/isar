from PyQt5 import QtCore
from PyQt5.QtCore import QAbstractTableModel, Qt


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

        if role == Qt.EditRole:
            try:
                prop: AnnotationProperty = self.__properties[index.row()]
                prop.set_value(value)
            except Exception as e:
                print("error", e)
                return False

        self.dataChanged.emit(index, index)
        return True

    def flags(self, index):
        return Qt.ItemIsSelectable | Qt.ItemIsEditable | Qt.ItemIsEnabled

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return ["Name", "Value"][section]


class AnnotationProperty:
    def __init__(self, name, value):
        self.name = name
        self._value = value

    def get_str_value(self):
        return str(self._value)

    def set_value(self, value):
        self._value = value

    def get_value(self):
        return self._value


class ColorAnnotationProperty(AnnotationProperty):
    def __init__(self, name, value):
        super().__init__(name, value)


class FilePathAnnotationProperty(AnnotationProperty):
    def __init__(self, name, value):
        super().__init__(name, value)


class PhysicalObjectAnnotationProperty(AnnotationProperty):
    def __init__(self, name, value):
        super().__init__(name, value)


class FloatTupleAnnotationProperty(AnnotationProperty):
    def __init__(self, name, value):
        super().__init__(name, value)


class IntTupleAnnotationProperty(AnnotationProperty):
    def __init__(self, name, value):
        super().__init__(name, value)


class FloatAnnotationProperty(AnnotationProperty):
    def __init__(self, name, value):
        super().__init__(name, value)


class IntAnnotationProperty(AnnotationProperty):
    def __init__(self, name, value):
        super().__init__(name, value)

    def set_value(self, value):
        self._value = int(value)


class BooleanAnnotationProperty(AnnotationProperty):
    def __init__(self, name, value):
        super().__init__(name, value)


class StringAnnotationProperty(AnnotationProperty):
    def __init__(self, name, value):
        super().__init__(name, value)
