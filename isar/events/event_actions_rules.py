import logging

from PyQt5 import uic, Qt, QtCore
from PyQt5.QtCore import QAbstractListModel, QModelIndex
from PyQt5.QtWidgets import QDialog

from isar.events import eventmanager, actionsservice

logger = logging.getLogger("isar.scene.physicalobjecttool")


class EventsActionsRulesDialog(QDialog):
    def __init__(self, scenes_model, annotations_model, phys_obj_model, parent=None):
        super().__init__(parent)

        self.scenes_model = scenes_model
        self.annotations_model = annotations_model
        self.physical_objects_model = phys_obj_model

        self.events_model = None
        self.events_scene = None

        self.actions_model = None
        self.actions_scene = None

        self.rules_model = None
        self.rules_scene = None

        self.event = None
        self.action = None
        self.rule = None

        self.init_ui()
        self.init_models()

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
        for ev_name, ev_type in eventmanager.event_types.items():
            self.event_type_combo.addItem(ev_name, ev_type)

        self.event_type_combo.currentIndexChanged.connect(self.event_type_combo_current_index_changed)

    def event_type_combo_current_index_changed(self, index):
        event_type = self.event_type_combo.itemData(index)
        self.update_event_properties_frame(event_type)

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
        action_type = self.action_type_combo.itemData(index)
        self.update_action_properties_frame(action_type)

    def update_action_properties_frame(self, action_type):
        logger.info("update_action_properties_frame")

    def event_select_target_btn_clicked(self):
        target = self.show_select_target_dialog()
        if target is not None:
            self.event.target = target

    def show_select_target_dialog(self):
        target = None
        target_type = self.event_type

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

