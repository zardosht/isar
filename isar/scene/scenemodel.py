import copy
import logging
import os

import jsonpickle
from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QAbstractListModel, QModelIndex

from isar.scene import sceneutil


logger = logging.getLogger("isar.scene.scenemodel")


class Project:
    def __init__(self):
        self.name = None
        self.base_path = None
        self.scenes = None


current_project: Project = None


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
                if sceneutil.is_valid_name(str(value)):
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
        if index is None:
            if self.scenes is not None:
                self.current_scene = self.scenes[0]
            self.endResetModel()
        else:
            self.dataChanged.emit(index, index, [Qt.DisplayRole])

    def set_current_scene(self, selected_index):
        self.current_scene = self.scenes[selected_index.row()]

    def save_project(self, parent_dir=None, project_name=None):
        new_project_created = False
        if current_project is None:
            create_project(parent_dir, project_name)
            new_project_created = True

        save_path = os.path.join(current_project.base_path, current_project.name + ".json")
        current_project.scenes = self.scenes
        frozen = jsonpickle.encode(current_project)
        with open(str(save_path), "w") as f:
             f.write(frozen)
        return new_project_created

    def load_project(self, project_dir, project_name):
        global current_project
        load_path = os.path.join(project_dir, project_name + ".json")
        with open(load_path, "r") as f:
            frozen = f.read()
            self.beginResetModel()
            current_project = jsonpickle.decode(frozen)
            self.scenes = current_project.scenes
            self.endResetModel()
            self.update_view(None)


class Scene:
    def __init__(self, name):
        self.name = name
        self.__physical_objects = []
        self.__annotations = []

    def add_physical_object(self, physical_obj):
        if not physical_obj in self.__physical_objects:
            self.__physical_objects.append(physical_obj)

    def delete_physical_object(self, phy_obj):
        if phy_obj in self.__physical_objects:
            self.__physical_objects.remove(phy_obj)
            phy_obj.delete_from_scene()

    def get_physical_objects(self):
        return tuple(self.__physical_objects)

    def add_annotation(self, annotation):
        if annotation not in self.__annotations:
            annotation.scene = self
            # annotation.owner = self
            self.__annotations.append(annotation)

    def remove_annotation(self, annotation):
        if annotation in self.__annotations:
            self.__annotations.remove(annotation)

    def delete_annotation(self, annotation):
        # annotation.owner = None
        if annotation in self.__annotations:
            self.__annotations.remove(annotation)
        else:
            for phys_obj in self.__physical_objects:
                phys_obj.remove_annotation(annotation)

    def get_scene_annotations(self):
        return self.__annotations

    def get_physical_object_annotations(self, phys_obj):
        pass

    def get_all_annotations(self):
        all_annotations = []
        all_annotations.extend(self.__annotations)
        for phys_obj in self.__physical_objects:
            all_annotations.extend(phys_obj.get_annotations())

        return tuple(all_annotations)


def create_project(parent_dir, project_name):
    global current_project
    project_dir = os.path.join(parent_dir, project_name)
    if not os.path.exists(project_dir):
        os.mkdir(project_dir)
        current_project = Project()
        current_project.name = project_name
        current_project.base_path = project_dir
        return True
    else:
        return False



