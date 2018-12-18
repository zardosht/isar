import copy

from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QAbstractListModel, QModelIndex

from isar.scene import util


class ScenesModel(QAbstractListModel):
    editCompleted = QtCore.pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.scenes = [Scene("New Scene")]
        self.current_scene = self.scenes[0]

    def rowCount(self, parent):
        return len(self.scenes)

    def data(self, index, role):
        if role == QtCore.Qt.DisplayRole:
            return self.scenes[index.row()].name

    def setData(self, index, value, role):
        if role == Qt.EditRole:
            new_name = self.scenes[index.row()].name
            try:
                if util.is_valid_name(str(value)):
                    new_name = str(value)
            except Exception as e:
                print("Error editing scene name", e)
                return False

            self.scenes[index.row()].name = new_name
            self.editCompleted.emit(new_name)

        return True  # edit was done correctly

    def flags(self, index):
        return Qt.ItemIsSelectable | Qt.ItemIsEditable | Qt.ItemIsEnabled

    def new_scene(self, at_index):
        self.beginInsertRows(QModelIndex(), at_index.row(), at_index.row())
        self.insertRow(at_index.row())
        new_scene = Scene("New Scene")
        self.scenes.append(new_scene)
        self.current_scene = new_scene
        self.endInsertRows()

    def clone_scene(self, selected_index):
        if len(self.scenes) <= selected_index.row():
            return

        self.beginInsertRows(QModelIndex(), selected_index.row(), selected_index.row())
        self.insertRow(selected_index.row())
        cloned_scene = copy.deepcopy(self.current_scene)
        cloned_scene.name = "Cloned - " + self.current_scene.name
        self.scenes.insert(selected_index.row() + 1, cloned_scene)
        self.endInsertRows()

    def delete_scene(self, selected_index):
        # TODO: remove properly using remove rows (see insert rows)

        if len(self.scenes) == 1:    # keep at least one scene
            return

        if len(self.scenes) <= selected_index.row():
            return

        del self.scenes[selected_index.row()]
        self.removeRow(selected_index.row())
        self.update_view(selected_index)

    def update_view(self, index):
        self.dataChanged.emit(index, index, [Qt.DisplayRole])

    def set_current_scene(self, selected_index):
        self.current_scene = self.scenes[selected_index.row()]


class Scene:
    def __init__(self, name):
        self.name = name
        self.__physical_objects = []
        self.__annotations = []

    def add_physical_object(self, physical_obj):
        self.__physical_objects.append(physical_obj)

    def get_physical_objects(self):
        return self.__physical_objects

    def add_annotation(self, annotation):
        self.__annotations.append(annotation)

    def get_annotations(self):
        return self.__annotations

