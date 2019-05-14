import copy
import logging
import os

import jsonpickle
from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QAbstractListModel, QModelIndex

from isar.events.actionsservice import ActionsService
from isar.scene import sceneutil

logger = logging.getLogger("isar.scene.scenemodel")


class Project:
    def __init__(self):
        self.name = None
        self.base_path = None
        self.scenes = None
        self.scene_size = None


current_project: Project = None


class ScenesModel(QAbstractListModel):
    editCompleted = QtCore.pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.scenes = [Scene("Scene1")]
        self.current_scene = self.scenes[0]
        self.scene_size = None

    def rowCount(self, parent):
        return len(self.scenes)

    def data(self, index, role):
        if role == QtCore.Qt.DisplayRole:
            return self.scenes[index.row()].name

    def setData(self, index, value, role):
        if role == Qt.EditRole:
            new_name = self.scenes[index.row()].name
            try:
                taken_names = [scene.name for scene in self.scenes]
                if sceneutil.is_valid_name(str(value), taken_names):
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
        scene_name = "Scene" + str(len(self.scenes) + 1)
        new_scene = Scene(scene_name)
        self.scenes.append(new_scene)
        self.current_scene = new_scene
        self.endInsertRows()

    def clone_scene(self, selected_index):
        if len(self.scenes) <= selected_index.row():
            return

        self.beginInsertRows(QModelIndex(), selected_index.row(), selected_index.row())
        self.insertRow(selected_index.row())

        cloned_scene = self.current_scene.clone()

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

        # first tell the current scene to update its phys_obj_annotations_dict
        self.current_scene.update_po_annotations_dict()

        # then change the current scene to new index
        self.current_scene = self.scenes[selected_index.row()]

        # in the new current scene, make all py
        self.current_scene.update_po_annotations()

    def save_project(self, parent_dir=None, project_name=None):
        new_project_created = False
        if current_project is None:
            create_project(parent_dir, project_name)
            current_project.scene_size = self.scene_size
            new_project_created = True

        save_path = os.path.join(current_project.base_path, current_project.name + ".json")

        for scene in self.scenes:
            scene.update_po_annotations_dict()

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
            for scene in self.scenes:
                scene.reset_runtime_state()

            # TODO: should it be called here? or somewhere else?

            ActionsService.init_defined_actions()

            self.endResetModel()
            self.update_view(None)


class Scene:
    def __init__(self, name):
        self.name = name
        self.__physical_objects = []
        self.__annotations = []
        self.__po_annotations_dict = {}

    def update_po_annotations_dict(self):
        self.__po_annotations_dict.clear()
        for phys_obj in self.__physical_objects:
            self.__po_annotations_dict[phys_obj.name] = phys_obj.get_annotations()

    def update_po_annotations(self):
        for physical_object in self.__physical_objects:
            physical_object.clear_annotations()
            for annotation in self.__po_annotations_dict[physical_object.name]:
                physical_object.add_annotation(annotation)

    def add_physical_object(self, physical_obj):
        if physical_obj not in self.__physical_objects:
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
        if not phys_obj in self.__po_annotations_dict:
            return None

        return tuple(self.__po_annotations_dict[phys_obj])

    def get_all_annotations(self):
        all_annotations = []
        all_annotations.extend(self.__annotations)
        for phys_obj in self.__physical_objects:
            all_annotations.extend(phys_obj.get_annotations())

        return tuple(all_annotations)

    def reset_runtime_state(self):
        for annotation in self.get_all_annotations():
            annotation.reset_runtime_state()

    def clone(self):
        cloned_scene = Scene("Cloned-" + self.name)
        cloned_scene.__annotations = []
        cloned_scene.__physical_objects = []
        for annotation in self.__annotations:
            cloned_annotation = copy.deepcopy(annotation)
            cloned_annotation.id = self.name + sceneutil.ANNOTATION_ID_SEPARATOR + cloned_annotation.name
            cloned_scene.add_annotation(annotation)

        for physical_object in self.__physical_objects:
            physical_object.clear_annotations()
            for annotation in physical_object.get_annotations():
                cloned_annotation = copy.deepcopy(annotation)
                cloned_annotation.id = self.name + sceneutil.ANNOTATION_ID_SEPARATOR + cloned_annotation.name
                physical_object.add_annotation(cloned_annotation)
            cloned_scene.add_physical_object(physical_object)

        return cloned_scene


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



