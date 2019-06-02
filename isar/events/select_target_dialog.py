import logging

from PyQt5 import uic
from PyQt5.QtWidgets import QDialog

from isar.events.events import SelectionEvent
from isar.scene.annotationmodel import Annotation
from isar.scene.physicalobjectmodel import PhysicalObject
from isar.scene.scenemodel import Scene


logger = logging.getLogger("isar.scene.select_target_dialog")


class SelectTargetDialog(QDialog):
    def __init__(self, scenes_model, parent=None):
        super().__init__(parent)

        self.target_type = None
        self.scene = None
        self.scenes_model = scenes_model
        self.targets_list = None

        self.return_only_names = False

        # the selected item in lists
        self.current_text = None
        self.__targets = []
        self.__target_names = []

        self.setup_ui()

    def set_target_types(self, target_type, event_type=None, action_type=None):
        if self.scene is None:
            logger.warning("The scene is not set for select event target dialog. Return.")
            return

        self.target_type = target_type
        self.target_type_label.setText(target_type.__name__ + "s: ")

        self.targets_list.clear()
        if issubclass(target_type, Annotation):
            all_scene_annotations = self.scene.get_all_annotations()
            for annotation in all_scene_annotations:
                if isinstance(annotation, target_type):
                    if event_type == SelectionEvent:
                        if annotation.is_selectable:
                            self.targets_list.addItem(annotation.name)
                    else:
                        self.targets_list.addItem(annotation.name)

        elif target_type == Scene:
            scenes = self.scenes_model.get_all_scenes()
            for scene in scenes:
                self.targets_list.addItem(scene.name)

        elif target_type == PhysicalObject:
            phys_objs = self.scene.get_physical_objects()
            for phys_obj in phys_objs:
                self.targets_list.addItem(phys_obj.name)

    def get_targets(self):
        self.__targets.clear()
        if self.return_only_names:
            return self.__target_names
        else:
            for target_name in self.__target_names:
                if self.target_type == Scene:
                    self.__targets.append(self.scenes_model.get_scene_by_name(target_name))
                elif self.target_type == PhysicalObject:
                    self.__targets.append(self.scene.get_physical_object_by_name(target_name))
                else:
                    self.__targets.append(self.scene.get_annotation_by_name(target_name))

            return self.__targets

    def targets_list_selection_changed(self):
        self.__target_names.clear()
        for item in self.targets_list.selectedItems():
            self.__target_names.append(item.text())

    def setup_ui(self):
        uic.loadUi("isar/ui/select_target_dialog.ui", self)
        self.targets_list.itemSelectionChanged.connect(self.targets_list_selection_changed)



