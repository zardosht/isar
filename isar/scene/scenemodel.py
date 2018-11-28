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


