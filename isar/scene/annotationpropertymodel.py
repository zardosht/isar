import logging
from ast import literal_eval
from PyQt5.QtCore import QAbstractTableModel, Qt, QModelIndex
from PyQt5.QtWidgets import QItemDelegate, QComboBox

from isar.scene.physicalobjectmodel import PhysicalObject

logger = logging.getLogger("isar.annotationpropertymodel")


def get_literal_from_str(str_val):
    value = None
    if isinstance(str_val, str):
        try:
            value = literal_eval(str_val)
        except Exception as e:
            logger.error("Error converting value:", e)
        finally:
            return value


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

    def get_annotation_property(self, index):
        if self.__properties is None:
            return

        return self.__properties[index.row()]

    def flags(self, index):
        if index.column() == 1:
            return Qt.ItemIsEditable | super().flags(index)
        return super().flags(index)

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return ["Name", "Value"][section]


class PhysicalObjectComboDelegate(QItemDelegate):
    def __init__(self):
        super().__init__()
        self.phys_obj_model = None
        self.combo_items = []

    def createEditor(self, parent, option, index: QModelIndex):
        if not self.phys_obj_model:
            return super().createEditor(parent, option, index)

        if index.column() != 1:
            return

        annotation_property = index.model().get_annotation_property(index)
        if isinstance(annotation_property, PhysicalObjectAnnotationProperty):
            combo = QComboBox(parent)
            self.combo_items.clear()
            self.combo_items.append(None)
            self.combo_items.extend(self.phys_obj_model.get_scene_physical_objects())
            combo.clear()
            for phys_obj in self.combo_items:
                if phys_obj is not None:
                    combo.addItem(phys_obj.name)
                else:
                    combo.addItem("None")

            if annotation_property.get_value() is None:
                combo.setCurrentIndex(0)
            else:
                index = -1
                for phys_obj in self.combo_items:
                    index += 1
                    if phys_obj is not None and phys_obj.name == annotation_property.get_value().name:
                        combo.setCurrentIndex(index)

            combo.currentIndexChanged.connect(self.current_index_changed)
            return combo
        else:
            return super().createEditor(parent, option, index)

    def setModelData(self, editor, model, index):
        if isinstance(editor, QComboBox):
            # TODO: find the property that requires a phys obj value and set its value
            annotation_property = index.model().get_annotation_property(index)
            if isinstance(annotation_property, PhysicalObjectAnnotationProperty):
                combo_index = editor.currentIndex()
                if combo_index == -1:
                    return
                phys_obj = self.combo_items[combo_index]
                model.setData(index, phys_obj, Qt.EditRole)
        else:
            super().setModelData(editor, model, index)

    def current_index_changed(self):
        self.commitData.emit(self.sender())


class AnnotationProperty:
    def __init__(self, name, value, annotation):
        self.name = name
        self._value = value
        self.annotation = annotation

    def get_str_value(self):
        return str(self._value)

    def set_value(self, value):
        raise TypeError("Must be implemented by subclasses")

    def get_value(self):
        return self._value


class ColorAnnotationProperty(AnnotationProperty):
    def __init__(self, name, value, annotation):
        super().__init__(name, value, annotation)

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
    pass


class PhysicalObjectAnnotationProperty(AnnotationProperty):
    def get_str_value(self):
        if self._value is None:
            return "None"
        else:
            return self._value.name

    def set_value(self, value):
        old_value = self._value
        if isinstance(value, PhysicalObject):
            value.annotations.append(self.annotation)
            self._value = value
            return True
        elif value is None:
            self._value = None
            if old_value is not None:
                old_value.annotations.remove(self.annotation)
            return True
        else:
            return False


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
    pass


class StringAnnotationProperty(AnnotationProperty):
    pass

