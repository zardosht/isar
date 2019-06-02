import logging

from PyQt5 import uic, Qt, QtCore
from PyQt5.QtCore import QAbstractListModel, QModelIndex
from PyQt5.QtWidgets import QDialog, QListWidget, QLabel, QVBoxLayout, QHBoxLayout, QDialogButtonBox, QWidget

from isar.events import actionsservice, events
from isar.events.actionsservice import Action
from isar.events.events import SelectionEvent, Event
from isar.events.rulesmanager import Rule
from isar.events.select_target_dialog import SelectTargetDialog
from isar.scene.annotationmodel import Annotation
from isar.scene.physicalobjectmodel import PhysicalObject
from isar.scene.scenemodel import Scene

logger = logging.getLogger("isar.scene.events_actions_rules")


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

        self.select_target_dialog = SelectTargetDialog(self.scenes_model, parent=self)

        self.events_scene = None
        self.event_type = None
        self.event_target = None
        self.event_name = None
        self.event = None
        self.scenes_combo_current_index_changed(0, "event_scenes_combo")
        self.event_type_combo_current_index_changed(0)

        self.actions_scene = None
        self.action_type = None
        self.action_name = None
        self.action = None
        self.scenes_combo_current_index_changed(0, "action_scenes_combo")
        self.action_type_combo_current_index_changed(0)

        self.rules_scene = None
        self.rule = None
        self.scenes_combo_current_index_changed(0, "rule_scenes_combo")

    def init_ui(self):
        uic.loadUi("isar/ui/events_actions_rules_dialog.ui", self)

        self.event_properties_frame.hide()

        self.init_scenes_combos()
        self.init_event_type_combo()
        self.init_action_type_combo()

        self.select_scene_event_target_btn.clicked.connect(lambda: self.select_event_target_btn_clicked(Scene))
        self.select_annotation_event_target_btn.clicked.connect(lambda: self.select_event_target_btn_clicked(Annotation))
        self.select_phys_obj_event_target_btn.clicked.connect(lambda: self.select_event_target_btn_clicked(PhysicalObject))

        self.add_event_btn.clicked.connect(self.add_event_btn_clicked)
        self.remove_event_btn.clicked.connect(self.remove_event_btn_clicked)

    def add_event_btn_clicked(self):
        if self.event_target is None:
            logger.warning("self.event_target is None. Return.")
            return

        if self.events_scene is None:
            logger.warning("self.events_scene is None. Return.")
            return

        if self.event is None:
            self.event = self.event_type(self.event_target)
            self.event.name = self.event_name
            self.event.scene_id = self.events_scene.name
            self.events_model.add_item(self.event)

    def remove_event_btn_clicked(self):
        index = self.events_list.selectionModel().currentIndex()
        self.events_model.remove_item(index)

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

            self.event = None
            self.event_type = None
            self.event_type_combo.setCurrentIndex(0)
            self.event_type_combo_current_index_changed(0)
            self.event_target = None
            self.event_name = None
            self.event_name_text.setText("")
            self.event_target_label.setText("... select event target ...")

        elif self.action_scenes_combo.objectName() == combo_name:
            scene = self.action_scenes_combo.itemData(index)
            self.actions_model.current_scene = scene
            self.actions_scene = scene

            self.action = None
            self.action_type = None
            self.action_type_combo_current_index_changed(0)
            self.action_name = None
            self.action_name_text.setText("")

        elif self.rule_scenes_combo.objectName() == combo_name:
            scene = self.rule_scenes_combo.itemData(index)
            self.rules_model.current_scene = scene
            self.rules_scene = scene
            self.rule_name_text.setText("")
            self.rule_event_name_label.setText(".... event name ...")
            self.rule_action_name_label.setText("... action name ...")

    def init_event_type_combo(self):
        for ev_name, ev_type in events.event_types.items():
            self.event_type_combo.addItem(ev_name, ev_type)

        self.event_type_combo.currentIndexChanged.connect(self.event_type_combo_current_index_changed)

    def event_type_combo_current_index_changed(self, index):
        self.event = None
        self.event_target = None
        self.event_name = None
        self.event_name_text.setText("")
        self.event_target_label.setText("... select event target ...")
        self.event_type = self.event_type_combo.itemData(index)
        self.update_event_properties_frame(self.event_type)
        event_target_types = self.event_type.target_types
        self.disable_all_event_target_selection_buttons()
        for target_type in event_target_types:
            if target_type == Scene:
                self.select_scene_event_target_btn.setEnabled(True)
            elif target_type == PhysicalObject:
                self.select_phys_obj_event_target_btn.setEnabled(True)
            else:
                self.select_annotation_event_target_btn.setEnabled(True)

    def disable_all_event_target_selection_buttons(self):
        self.select_scene_event_target_btn.setEnabled(False)
        self.select_annotation_event_target_btn.setEnabled(False)
        self.select_phys_obj_event_target_btn.setEnabled(False)

    def update_event_properties_frame(self, event_type):
        if event_type.has_properties:
            self.event_properties_frame.show()
            event_type.update_event_properties_frame(event_type, self.event_properties_frame)
        else:
            self.event_properties_frame.hide()

    def init_action_type_combo(self):
        for ac_name, ac_type in actionsservice.action_types.items():
            self.action_type_combo.addItem(ac_name, ac_type)

        self.action_type_combo.currentIndexChanged.connect(self.action_type_combo_current_index_changed)

    def action_type_combo_current_index_changed(self, index):
        self.action = None
        self.action_name = None
        self.action_name_text.setText("")

        # TODO: reset other properites of action

        self.action_type = self.action_type_combo.itemData(index)
        self.update_action_properties_frame(self.action_type)

    def update_action_properties_frame(self, action_type):
        logger.info("update_action_properties_frame")

    def select_event_target_btn_clicked(self, target_type):
        if self.event_type is None:
            logger.warning("self.event_type is None. Setting to default SelectionEvent")
            self.event_type = SelectionEvent

        if len(self.event_type.target_types) == 1:
            target_type = self.event_type.target_types[0]

        targets = self.show_select_target_dialog(target_type, self.event_type)

        if targets is not None and len(targets) > 0:
            target = targets[0]
            logger.info("received event target: {}".format(str(target)))
            self.event_target = target
            self.event_name = "On_" + self.event_target.name + "_" + self.event_type.__name__
            self.event_name_text.setText(self.event_name)
            if isinstance(target, Scene):
                self.event_target_label.setText(target.name)
            else:
                self.event_target_label.setText(self.events_scene.name + "." + target.name)
        else:
            logger.warning("target is none")

    def show_select_target_dialog(self, target_type,
                                  event_type=None, action_type=None,
                                  return_only_names=False, multiple_selection=False):
        targets = None
        self.select_target_dialog.scene = self.events_scene
        self.select_target_dialog.set_target_types(target_type, event_type, action_type)
        self.select_target_dialog.return_only_names = return_only_names
        self.select_target_dialog.setModal(True)
        self.select_target_dialog.exec()
        if self.select_target_dialog.result() == QDialog.Accepted:
            targets = self.select_target_dialog.get_targets()

        return targets

    def init_models(self):
        self.events_model = ItemsModel(ItemsModel.EVENTS)
        self.events_list.setModel(self.events_model)

        self.actions_model = ItemsModel(ItemsModel.ACTIONS)
        self.actions_list.setModel(self.actions_model)

        self.rules_model = ItemsModel(ItemsModel.RULES)
        self.rules_list.setModel(self.rules_model)


class ItemsModel(QAbstractListModel):
    EVENTS = 0
    ACTIONS = 1
    RULES = 2

    def __init__(self, item_type):
        super().__init__()
        self.item_type = item_type
        self.current_scene = None

    def rowCount(self, parent=None):
        if self.current_scene is not None:
            if self.item_type == ItemsModel.EVENTS:
                return len(self.current_scene.get_events())
            elif self.item_type == ItemsModel.ACTIONS:
                return len(self.current_scene.get_actions())
            elif self.item_type == ItemsModel.RULES:
                return len(self.current_scene.get_rules())
            else:
                return 0
        else:
            return 0

    def data(self, index, role):
        item = index.internalPointer()
        if role == QtCore.Qt.DisplayRole:
            return item.name
        elif role == QtCore.Qt.UserRole:
            return item

    def flags(self, index):
        return QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled

    def add_item(self, item):
        last_index = self.rowCount()
        self.beginInsertRows(QModelIndex(), last_index, last_index + 1)
        if self.current_scene is not None:
            if self.item_type == ItemsModel.EVENTS:
                if isinstance(item, Event):
                    self.current_scene.add_event(item)
            elif self.item_type == ItemsModel.ACTIONS:
                if isinstance(item, Action):
                    self.current_scene.add_action(item)
            elif self.item_type == ItemsModel.RULES:
                if isinstance(item, Rule):
                    self.current_scene.add_rule(item)
        else:
            logger.warning("current_scene is None!")
        self.endInsertRows()

    def remove_item(self, index):
        self.beginRemoveRows(QModelIndex(), index.row(), index.row())
        item = index.internalPointer()
        if self.current_scene is not None:
            if self.item_type == ItemsModel.EVENTS:
                if isinstance(item, Event):
                    self.current_scene.remove_event(item)
            elif self.item_type == ItemsModel.ACTIONS:
                if isinstance(item, Action):
                    self.current_scene.remove_action(item)
            elif self.item_type == ItemsModel.RULES:
                if isinstance(item, Rule):
                    self.current_scene.remove_rule(item)
        else:
            logger.warning("current_scene is None!")
        self.endRemoveRows()

    def index(self, row, column, parent):
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        if self.current_scene is not None:
            if self.item_type == ItemsModel.EVENTS:
                items = self.current_scene.get_events()
            elif self.item_type == ItemsModel.ACTIONS:
                items = self.current_scene.get_actions()
            elif self.item_type == ItemsModel.RULES:
                items = self.current_scene.get_rules()
        else:
            logger.warning("current_scene is None!")

        item = items[row]
        return self.createIndex(row, 0, item)


