import logging

from PyQt5 import uic, Qt, QtCore
from PyQt5.QtCore import QAbstractListModel, QModelIndex
from PyQt5.QtWidgets import QDialog, QListWidget, QLabel, QVBoxLayout, QHBoxLayout, QDialogButtonBox, QWidget

from isar.events import actionsservice, events
from isar.scene.annotationmodel import Annotation
from isar.scene.physicalobjectmodel import PhysicalObject
from isar.scene.scenemodel import Scene

logger = logging.getLogger("isar.scene.physicalobjecttool")


"""

* get rid of global event, actions, and rules.
* Every event, action, or rule is defined only on one scene (the one user chooses) 
and is only available/active on this scene. 
* If the target of an event or action is an annotation, or physical object, 
only those annotations and physical objects of the selected scene can be chosen as target.

"""


class EventsActionsRulesDialog(QDialog):
    def __init__(self, scenes_model, annotations_model, phys_obj_model, parent=None):
        super().__init__(parent)

        self.scenes_model = scenes_model
        self.annotations_model = annotations_model
        self.physical_objects_model = phys_obj_model

        self.events_model = None
        self.actions_model = None
        self.rules_model = None

        self.init_ui()
        self.init_models()

        self.select_event_target_dialog = SelectTargetDialog(self.scenes_model, parent=self)

        self.events_scene = None
        self.event_type = None
        self.event = None
        self.scenes_combo_current_index_changed(0, "event_scenes_combo")
        self.event_type_combo_current_index_changed(0)

        self.actions_scene = None
        self.action_type = None
        self.action = None
        self.scenes_combo_current_index_changed(0, "action_scenes_combo")

        self.rules_scene = None
        self.rule = None
        self.scenes_combo_current_index_changed(0, "rule_scenes_combo")

    def init_ui(self):
        uic.loadUi("isar/ui/events_actions_rules_dialog.ui", self)

        self.event_properties_frame.hide()

        self.init_scenes_combos()
        self.init_event_type_combo()
        self.init_action_type_combo()

        self.event_select_target_btn.clicked.connect(self.event_select_target_btn_clicked)

    def init_scenes_combos(self):
        scene_combos = [self.event_scenes_combo, self.action_scenes_combo, self.rule_scenes_combo]
        scenes = self.scenes_model.get_all_scenes()
        for combo in scene_combos:
            for scene in scenes:
                combo.addItem(scene.name, scene)

        self.event_scenes_combo.currentIndexChanged.connect(
            lambda index: self.scenes_combo_current_index_changed(index, "event_scenes_combo"))
        self.action_scenes_combo.currentIndexChanged.connect(
            lambda index: self.scenes_combo_current_index_changed(index, "action_scenes_combo"))
        self.rule_scenes_combo.currentIndexChanged.connect(
            lambda index: self.scenes_combo_current_index_changed(index, "rule_scenes_combo"))

    def scenes_combo_current_index_changed(self, index, combo_name):
        if self.event_scenes_combo.objectName() == combo_name:
            scene = self.event_scenes_combo.itemData(index)
            self.events_model.current_scene = scene
            self.events_scene = scene
        elif self.action_scenes_combo.objectName() == combo_name:
            scene = self.action_scenes_combo.itemData(index)
            self.actions_model.current_scene = scene
            self.actions_scene = scene
        elif self.rule_scenes_combo.objectName() == combo_name:
            scene = self.rule_scenes_combo.itemData(index)
            self.rules_model.current_scene = scene
            self.rules_scene = scene

    def init_event_type_combo(self):
        for ev_name, ev_type in events.event_types.items():
            self.event_type_combo.addItem(ev_name, ev_type)

        self.event_type_combo.currentIndexChanged.connect(self.event_type_combo_current_index_changed)

    def event_type_combo_current_index_changed(self, index):
        self.event_type = self.event_type_combo.itemData(index)
        self.update_event_properties_frame(self.event_type)

    def update_event_properties_frame(self, event_type):
        if event_type.has_properties:
            self.event_properties_frame.show()
            event_type.update_event_properties_frame(self.event_properties_frame)
        else:
            self.event_properties_frame.hide()

    def init_action_type_combo(self):
        for ac_name, ac_type in actionsservice.action_types.items():
            self.action_type_combo.addItem(ac_name, ac_type)

        self.action_type_combo.currentIndexChanged.connect(self.action_type_combo_current_index_changed)

    def action_type_combo_current_index_changed(self, index):
        self.action_type = self.action_type_combo.itemData(index)
        self.update_action_properties_frame(self.action_type)

    def update_action_properties_frame(self, action_type):
        logger.info("update_action_properties_frame")

    def event_select_target_btn_clicked(self):
        target = self.show_select_event_target_dialog()
        if target is not None:
            self.event.target = target

    def show_select_event_target_dialog(self):
        target = None
        self.select_event_target_dialog.scene = self.events_scene
        self.select_event_target_dialog.set_target_types(self.event_type.target_types)
        self.select_event_target_dialog.setModal(True)
        self.select_event_target_dialog.show()
        if self.select_event_target_dialog.result() == QDialog.Accepted:
            target = self.select_event_target_dialog.get_event_target()

        return target

    def init_models(self):
        self.events_model = ItemsModel()
        self.events_list.setModel(self.events_model)

        self.actions_model = ItemsModel()
        self.actions_list.setModel(self.actions_model)

        self.rules_model = ItemsModel()
        self.rules_list.setModel(self.rules_model)


class ItemsModel(QAbstractListModel):
    def __init__(self):
        super().__init__()
        self.items = []
        self.current_scene = None

    def rowCount(self, parent=None):
        return len(self.items)

    def data(self, index, role):
        item = index.internalPointer()
        if role == QtCore.Qt.DisplayRole:
            return item.name
        elif role == QtCore.Qt.UserRole:
            return item

    def flags(self, index):
        return Qt.ItemIsSelectable | Qt.ItemIsEnabled

    def add_item(self, item):
        self.items.append(item)

    def index(self, row, column, parent):
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        item = self.items[row]
        return self.createIndex(row, 0, item)


class SelectTargetDialog(QDialog):
    SCENES_TAB = 0
    ANNOTATIONS_TAB = 1
    PHYS_OBJS_TAB = 2

    def __init__(self, scenes_model, parent=None):
        super().__init__(parent)

        self.scene = None
        self.scenes_model = scenes_model
        self.scenes_list = None
        self.annotations_list = None
        self.phys_objs_list = None

        # the selected item in lists
        self.current_text = None
        self.event_target = None

        self.setup_ui()

    def set_target_types(self, target_types):
        if self.scene is None:
            logger.warning("The scene is not set for select event target dialog. Return.")
            return

        if len(target_types) == 1:
            target_type = target_types[0]
            if issubclass(target_type, Annotation):
                all_scene_annotations = self.scene.get_all_annotations()
                for annotation in all_scene_annotations:
                    if isinstance(annotation, target_type):
                        self.annotations_list.addItem(annotation.name)

                self.tabWidget.setTabEnabled(SelectTargetDialog.SCENES_TAB, False);
                self.tabWidget.setTabEnabled(SelectTargetDialog.ANNOTATIONS_TAB, True);
                self.tabWidget.setTabEnabled(SelectTargetDialog.PHYS_OBJS_TAB, False);
            elif target_type == Scene:
                scenes = self.scenes_model.get_all_scenes()
                for scene in scenes:
                    self.scenes_list.addItem(scene.name)

                self.tabWidget.setTabEnabled(SelectTargetDialog.SCENES_TAB, True);
                self.tabWidget.setTabEnabled(SelectTargetDialog.ANNOTATIONS_TAB, False);
                self.tabWidget.setTabEnabled(SelectTargetDialog.PHYS_OBJS_TAB, False);
            elif target_type == PhysicalObject:
                phys_objs = self.scene.get_physical_objects()
                for phys_obj in phys_objs:
                    self.phys_objs_list.addItem(phys_obj.name)

                self.tabWidget.setTabEnabled(SelectTargetDialog.SCENES_TAB, False);
                self.tabWidget.setTabEnabled(SelectTargetDialog.ANNOTATIONS_TAB, False);
                self.tabWidget.setTabEnabled(SelectTargetDialog.PHYS_OBJS_TAB, True);
        elif len(target_types) == 2:
            all_scene_annotations = self.scene.get_all_annotations()
            for annotation in all_scene_annotations:
                self.annotations_list.addItem(annotation.name)

            phys_objs = self.scene.get_physical_objects()
            for phys_obj in phys_objs:
                self.phys_objs_list.addItem(phys_obj.name)

            self.tabWidget.setTabEnabled(SelectTargetDialog.SCENES_TAB, False);
            self.tabWidget.setTabEnabled(SelectTargetDialog.ANNOTATIONS_TAB, True);
            self.tabWidget.setTabEnabled(SelectTargetDialog.PHYS_OBJS_TAB, True);

    def get_event_target(self):
        if self.tabWidget.currentIndex() == SelectTargetDialog.SCENES_TAB:
            self.event_target = self.event_target = self.scenes_model.get_scene_by_name(self.current_text)
        elif self.tabWidget.currentIndex() == SelectTargetDialog.ANNOTATIONS_TAB:
            self.event_target = self.scene.get_annotation_by_name(self.current_text)
        else:
            self.event_target = self.scene.get_physical_object_by_name(self.current_text)

        return self.event_target

    def target_list_current_text_changed(self, current_text):
        self.current_text = current_text

    def setup_ui(self):
        uic.loadUi("isar/ui/select_event_target_dialog.ui", self)
        self.scenes_list.currentTextChanged.connect(self.target_list_current_text_changed)
        self.annotations_list.currentTextChanged.connect(self.target_list_current_text_changed)
        self.phys_objs_list.currentTextChanged.connect(self.target_list_current_text_changed)



