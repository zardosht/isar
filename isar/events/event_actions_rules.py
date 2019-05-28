import logging

from PyQt5 import uic, Qt, QtCore
from PyQt5.QtCore import QAbstractListModel, QModelIndex
from PyQt5.QtWidgets import QDialog

from isar.events import eventmanager, actionsservice

logger = logging.getLogger("isar.scene.physicalobjecttool")


GLOBAL_SCENE_ID = "GLOBAL"


class EventsActionsRulesDialog(QDialog):
    def __init__(self, scenes_model, annotations_model, phys_obj_model, parent=None):
        super().__init__(parent)

        self.scenes_model = scenes_model
        self.annotations_model = annotations_model
        self.physical_objects_model = phys_obj_model

        self.scene_events_model = None
        self.global_events_model = None

        self.scene_actions_model = None
        self.global_actions_model = None

        self.scene_rules_model = None
        self.global_rules_model = None

        self.init_ui()
        self.init_models()
        self.init_signals()

    def init_ui(self):
        uic.loadUi("isar/ui/events_actions_rules_dialog.ui", self)
        self.init_scenes_combos()
        self.init_event_type_combo()
        self.init_action_type_combo()

    def init_scenes_combos(self):
        scene_combos = [self.event_scenes_combo, self.action_scenes_combo, self.rule_scenes_combo]
        scenes = self.scenes_model.get_all_scenes()
        for combo in scene_combos:
            combo.addItem(GLOBAL_SCENE_ID, None)
            for scene in scenes:
                combo.addItem(scene.name, scene)

    def init_event_type_combo(self):
        for ev_name, ev_type in eventmanager.event_types.items():
            self.event_type_combo.addItem(ev_name, ev_type)

        self.event_type_combo.currentIndexChanged.connect(self.event_type_combo_current_index_changed)

    def event_type_combo_current_index_changed(self, index):
        event_type = self.event_type_combo.itemData(index)
        self.update_event_properties_frame(event_type)

    def update_event_properties_frame(self, event_type):
        # event_type.update_event_properties_frame(self.event_properties_frame)
        logger.info("update_event_properties_frame")

    def init_action_type_combo(self):
        for ac_name, ac_type in actionsservice.action_types.items():
            self.action_type_combo.addItem(ac_name, ac_type)

        self.action_type_combo.currentIndexChanged.connect(self.action_type_combo_current_index_changed)

    def action_type_combo_current_index_changed(self, index):
        action_type = self.action_type_combo.itemData(index)
        self.update_action_properties_frame(action_type)

    def update_action_properties_frame(self, action_type):
        logger.info("update_action_properties_frame")

    def init_signals(self):
        pass

    def init_models(self):
        self.scene_events_model = ItemsModel()
        self.scene_events_list.setModel(self.scene_events_model)
        self.global_events_model = ItemsModel(for_global_list=True)
        self.global_events_list.setModel(self.global_events_model)

        self.scene_actions_model = ItemsModel()
        self.scene_actions_list.setModel(self.scene_actions_model)
        self.global_actions_model = ItemsModel(for_global_list=True)
        self.global_actions_list.setModel(self.global_actions_model)

        self.scene_rules_model = ItemsModel()
        self.scene_rules_list.setModel(self.scene_rules_model)
        self.global_rules_model = ItemsModel(for_global_list=True)
        self.global_rules_list.setModel(self.global_rules_model)


class ItemsModel(QAbstractListModel):
    def __init__(self, for_global_list=False):
        super().__init__()
        self.for_global_list = for_global_list
        self.scene_items = []
        self.global_items = []

    def rowCount(self, parent=None):
        if self.for_global_list:
            return len(self.global_items)
        else:
            return len(self.scene_items)

    def data(self, index, role):
        item = index.internalPointer()
        if role == QtCore.Qt.DisplayRole:
            return item.name
        elif role == QtCore.Qt.UserRole:
            return item

    def flags(self, index):
        return Qt.ItemIsSelectable | Qt.ItemIsEnabled

    def add_item(self, item):
        if item.scene_id == GLOBAL_SCENE_ID:
            self.global_items.append(item)
        else:
            self.scene_items.append(item)

    def index(self, row, column, parent):
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        if self.for_global_list:
            item = self.global_items[row]
        else:
            item = self.scene_items[row]

        return self.createIndex(row, 0, item)

