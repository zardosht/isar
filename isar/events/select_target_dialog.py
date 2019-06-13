import logging

from PyQt5 import uic, QtCore
from PyQt5.QtWidgets import QDialog, QListWidgetItem

from isar.events.actions import Action
from isar.events.events import SelectionEvent, Event
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

        # the selected item in lists
        self.__targets = []

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
                            lw_item = self.create_list_widget_item(annotation.name, annotation)
                            self.targets_list.addItem(lw_item)
                    else:
                        lw_item = self.create_list_widget_item(annotation.name, annotation)
                        self.targets_list.addItem(lw_item)

        elif target_type == Scene:
            scenes = self.scenes_model.get_all_scenes()
            for scene in scenes:
                lw_item = self.create_list_widget_item(scene.name, scene)
                self.targets_list.addItem(lw_item)

        elif target_type == PhysicalObject:
            phys_objs = self.scene.get_physical_objects()
            for phys_obj in phys_objs:
                lw_item = self.create_list_widget_item(phys_obj.name, phys_obj)
                self.targets_list.addItem(lw_item)

        elif target_type == Action:
            actions = self.scene.get_actions()
            for action in actions:
                lw_item = self.create_list_widget_item(action.name, action)
                self.targets_list.addItem(lw_item)

        elif target_type == Event:
            events = self.scene.get_events()
            for event in events:
                lw_item = self.create_list_widget_item(event.name, event)
                self.targets_list.addItem(lw_item)

    @staticmethod
    def create_list_widget_item(text, data):
        lw_item = QListWidgetItem(text)
        lw_item.setData(QtCore.Qt.UserRole, data)
        return lw_item

    def get_targets(self):
        return self.__targets

    def targets_list_selection_changed(self):
        self.__targets.clear()
        for item in self.targets_list.selectedItems():
            self.__targets.append(item.data(QtCore.Qt.UserRole))

    def setup_ui(self):
        uic.loadUi("isar/ui/select_target_dialog.ui", self)
        self.targets_list.itemSelectionChanged.connect(self.targets_list_selection_changed)
