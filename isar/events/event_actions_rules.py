import logging

from PyQt5 import uic, Qt, QtCore
from PyQt5.QtCore import QAbstractListModel, QModelIndex
from PyQt5.QtWidgets import QDialog


logger = logging.getLogger("isar.scene.physicalobjecttool")


GLOBAL_SCENE_NAME = "global"

class EventsActionsRulesDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.scenes_model = None
        self.annotations_model = None
        self.physical_objects_model = None

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

    def init_models(self):
        self.scene_events_model = EventsModel()
        self.scene_events_list.setMode(self.scene_events_model)
        self.global_events_model = EventsModel(for_global_list=True)
        self.global_events_list.setMode(self.global_events_model)

        self.scene_actions_model = ActionsModel()
        self.scene_actions_list.setMode(self.scene_actions_model)
        self.global_actions_model = ActionsModel(for_global_list=True)
        self.global_actions_list.setMode(self.global_actions_model)

        self.scene_rules_model = RulesModel()
        self.scene_rules_list.setMode(self.scene_rules_model)
        self.global_rules_model = RulesModel(for_global_list=True)
        self.global_rules_list.setMode(self.global_rules_model)


class EventsModel(QAbstractListModel):
    def __init__(self, for_global_list=False):
        self.for_global_list = for_global_list
        self.scene_events = []
        self.global_events = []

    def rowCount(self, parent=None):
        if self.for_global_list:
            return len(self.global_events)
        else:
            return len(self.scene_events)

    def data(self, index, role):
        event = index.internalPointer()
        if role == QtCore.Qt.DisplayRole:
            return event.name
        elif role == QtCore.Qt.UserRole:
            return event

    def flags(self, index):
        return Qt.ItemIsSelectable | Qt.ItemIsEnabled

    def add_event(self, event):
        if event.scene_name == GLOBAL_SCENE_NAME:
            self.global_events.append(event)
        else:
            self.scene_events.append(event)

    def index(self, row, column, parent):
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        if self.for_global_list:
            event = self.global_events[row]
        else:
            event = self.scene_events[row]

        return self.createIndex(row, 0, event)


class ActionsModel(QAbstractListModel):
    def __init__(self, for_global_list=False):
        self.for_global_list = for_global_list
        self.scene_actions = []
        self.global_actions = []

    def rowCount(self, parent=None):
        if self.for_global_list:
            return len(self.global_actions)
        else:
            return len(self.scene_actions)

    def data(self, index, role):
        action = index.internalPointer()
        if role == QtCore.Qt.DisplayRole:
            return action.name
        elif role == QtCore.Qt.UserRole:
            return action

    def flags(self, index):
        return Qt.ItemIsSelectable | Qt.ItemIsEnabled

    def add_action(self, action):
        if action.scene_name == GLOBAL_SCENE_NAME:
            self.global_actions.append(action)
        else:
            self.scene_actions.append(action)

    def index(self, row, column, parent):
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        if self.for_global_list:
            action = self.global_actions[row]
        else:
            action = self.scene_actions[row]

        return self.createIndex(row, 0, action)


class RulesModel(QAbstractListModel):
    def __init__(self, for_global_list=False):
        self.for_global_list = for_global_list
        self.scene_rules = []
        self.global_rules = []

    def rowCount(self, parent=None):
        if self.for_global_list:
            return len(self.global_rules)
        else:
            return len(self.scene_rules)

    def data(self, index, role):
        rule = index.internalPointer()
        if role == QtCore.Qt.DisplayRole:
            return rule.name
        elif role == QtCore.Qt.UserRole:
            return rule

    def flags(self, index):
        return Qt.ItemIsSelectable | Qt.ItemIsEnabled

    def add_rule(self, rule):
        if rule.scene_name == GLOBAL_SCENE_NAME:
            self.global_rules.append(rule)
        else:
            self.scene_rules.append(rule)

    def index(self, row, column, parent):
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        if self.for_global_list:
            rule = self.global_rules[row]
        else:
            rule = self.scene_rules[row]

        return self.createIndex(row, 0, rule)

