import copy
import logging
import os
import time

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
    scene_changed = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()
        self.scenes = [Scene("Scene1")]
        self.__current_scene = self.scenes[0]
        self.scene_size = None
        self.back_scene_nav_stack = [self.scenes[0].name]
        self.default_scene_navigation_flow = None
        self.scene_navigation_flow = None

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
            self.default_scene_navigation_flow = self.get_ordered_scene_ids()
            self.editCompleted.emit(new_name)

        return True  # edit was done correctly

    def find_index(self, scn):
        idx = -1
        try:
            idx = self.scenes.index(scn)
        except ValueError:
            logger.warning("Scene not found")

        if idx != -1:
            return self.createIndex(idx, 0)

    def flags(self, index):
        return Qt.ItemIsSelectable | Qt.ItemIsEditable | Qt.ItemIsEnabled

    def new_scene(self, at_index):
        self.beginInsertRows(QModelIndex(), at_index.row(), at_index.row())
        self.insertRow(at_index.row())
        scene_name = "Scene" + str(len(self.scenes) + 1)
        new_scene = Scene(scene_name)

        index = at_index.row() + 1
        if index <= len(self.scenes):
            self.scenes.insert(index, new_scene)

        qmodel_index = self.createIndex(index, index)
        self.set_current_scene(qmodel_index)
        self.back_scene_nav_stack.append(self.__current_scene.name)
        self.endInsertRows()

    def clone_scene(self, selected_index):
        if len(self.scenes) <= selected_index.row():
            return

        self.beginInsertRows(QModelIndex(), selected_index.row(), selected_index.row())
        self.insertRow(selected_index.row())

        cloned_scene = self.__current_scene.clone()

        self.scenes.insert(selected_index.row() + 1, cloned_scene)
        self.default_scene_navigation_flow = self.get_ordered_scene_ids()
        self.endInsertRows()

    def delete_scene(self, selected_index):
        if len(self.scenes) == 1:    # keep at least one scene
            return

        index = selected_index.row()
        if len(self.scenes) <= index:
            return

        scene_to_delete = self.scenes[index]
        self.back_scene_nav_stack = [scene_name
                                     for scene_name in self.back_scene_nav_stack
                                     if scene_name != scene_to_delete.name]

        del self.scenes[index]
        self.removeRow(index)

        if index == 0:
            self.set_current_scene(self.createIndex(index, index))
        else:
            self.set_current_scene(self.createIndex(index - 1, index - 1))

        self.update_view(selected_index)

    def update_view(self, index):
        if index is None:
            if self.scenes is not None:
                index = self.createIndex(0, 0)
                self.set_current_scene(index)
            self.endResetModel()
        else:
            self.dataChanged.emit(index, index, [Qt.DisplayRole])

    def set_current_scene(self, selected_index):

        # first tell the current scene to update its phys_obj_annotations_dict
        self.__current_scene.update_po_annotations_dict()

        # then change the current scene to new index
        self.__current_scene = self.scenes[selected_index.row()]

        # in the new current scene, make all py
        self.__current_scene.update_po_annotations()

        if len(self.back_scene_nav_stack) == 0:
            self.back_scene_nav_stack.append(self.__current_scene.name)
        elif self.back_scene_nav_stack[-1] != self.__current_scene.name:
            self.back_scene_nav_stack.append(self.__current_scene.name)

        self.default_scene_navigation_flow = self.get_ordered_scene_ids()

        print("scene navigation: " + str(self.back_scene_nav_stack))

        self.scene_changed.emit()

    def move_scene_down(self, selected_index):
        index = selected_index.row()
        if index >= len(self.scenes) - 1:
            return

        if index + 1 >= len(self.scenes):
            return

        self.scenes[index + 1], self.scenes[index] = self.scenes[index], self.scenes[index + 1]
        self.default_scene_navigation_flow = self.get_ordered_scene_ids()

        self.set_current_scene(self.createIndex(index + 1, index + 1))

        self.update_view(selected_index)

    def move_scene_up(self, selected_index):
        index = selected_index.row()
        if index == 0:
            return

        self.scenes[index - 1], self.scenes[index] = self.scenes[index], self.scenes[index - 1]
        self.default_scene_navigation_flow = self.get_ordered_scene_ids()

        self.set_current_scene(self.createIndex(index - 1, index - 1))

        self.update_view(selected_index)

    def set_scene_navigation_flow(self, navigation_flow):
        self.scene_navigation_flow = navigation_flow

    def get_ordered_scene_ids(self):
        result = []
        for scene in self.scenes:
            result.append(scene.name)
        return result

    def get_current_scene(self):
        return self.__current_scene

    def show_scene(self, scene_name):
        for idx, scene in enumerate(self.scenes):
            if scene.name == scene_name:
                index = self.createIndex(idx, 0)
                self.set_current_scene(index)
                break

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

            self.back_scene_nav_stack.clear()
            # for scene in self.scenes:
            #     self.scene_navigation.append(scene.name)
            self.show_scene(self.scenes[0].name)

            self.endResetModel()


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
        cloned_scene = Scene("Cloned-" + self.name + str(time.time()))
        cloned_scene.__annotations = []
        cloned_scene.__physical_objects = []
        cloned_scene.__po_annotations_dict = {}

        for annotation in self.__annotations:
            cloned_annotation = copy.deepcopy(annotation)
            cloned_annotation.id = cloned_scene.name + sceneutil.ANNOTATION_ID_SEPARATOR + cloned_annotation.name
            cloned_scene.add_annotation(cloned_annotation)

        for po in self.__physical_objects:
            po_annotations = []
            if po.name in self.__po_annotations_dict:
                po_annotations = self.__po_annotations_dict[po.name]

            cloned_po_annotations = []
            for annotation in po_annotations:
                cloned_annotation = copy.deepcopy(annotation)
                cloned_annotation.scene = cloned_scene
                cloned_annotation.id = cloned_scene.name + sceneutil.ANNOTATION_ID_SEPARATOR + cloned_annotation.name
                cloned_po_annotations.append(cloned_annotation)

            cloned_scene.__po_annotations_dict[po.name] = cloned_po_annotations
            cloned_scene.add_physical_object(po)

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



