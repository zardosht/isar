import functools
import logging
import os
import time
from threading import Thread

from PyQt5 import uic, QtCore, QtWidgets, QtGui
from PyQt5.QtCore import QTimer, QItemSelectionModel, Qt, QItemSelection
from PyQt5.QtGui import QPixmap, QMouseEvent, QDrag
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QListView, QFileDialog, QMessageBox, QInputDialog, QMainWindow

import isar
from isar.camera.camera import CameraService
from isar.events.events_actions_rules import EventsActionsRulesDialog
from isar.scene import sceneutil, scenemodel
from isar.scene.annotationmodel import AnnotationPropertiesModel, AnnotationPropertyItemDelegate
from isar.scene.annotationmodel import AnnotationsModel
from isar.scene.cameraview import CameraView
from isar.scene.physicalobjectmodel import PhysicalObjectsModel, PhysicalObject
from isar.scene.scenemodel import ScenesModel
from isar.services import servicemanager
from isar.services.servicemanager import ServiceNames
from isar.tracking.selectionstick import SelectionStickService

logger = logging.getLogger("isar.scene.definitionwindow")


class SceneDefinitionWindow(QMainWindow):

    SELECT_BTN_ID = 10

    def __init__(self):
        super().__init__()
        self.camera_view = None
        self.objects_view = None
        self.setup_ui()

        self._camera_service: CameraService = None
        self.setup_camera_service()

        self.scene_size_initialized = False
        self.scene_rect = None
        self.scene_size = None
        self.scene_scale_factor_c = None

        self._object_detection_service = None
        self._selection_stick_service: SelectionStickService = None
        self._hand_tracking_service = None
        self.setup_object_detection_service()

        self.setAttribute(QtCore.Qt.WA_QuitOnClose, True)

        self.scenes_model = None
        self.physical_objects_model = None
        self.annotations_model = None
        self.setup_models()

        self.setup_signals()

        self._camera_view_timer = None
        self._object_detection_timer = None
        self.setup_timer()

    def setup_ui(self):
        # uic.loadUi("isar/ui/scene_definition.ui", self)

        self.setupUi(self)

        self.mouse_object_position_label.setText("")
        self.mouse_image_position_label.setText("")

        self.properties_view.horizontalHeader().setStretchLastSection(True)
        self.properties_view.resizeRowsToContents()

        self.camera_view_container.setLayout(QHBoxLayout())
        self.camera_view = CameraView(self.camera_view_container, self)
        self.camera_view_container.layout().setContentsMargins(0, 0, 0, 0)
        self.camera_view_container.layout().addWidget(self.camera_view, stretch=1)

        self.annotation_buttons.setId(self.select_btn, SceneDefinitionWindow.SELECT_BTN_ID)
        self.select_btn.setChecked(True)

        self.objects_view = PhysicalObjectsView(self)
        self.objects_view.setObjectName("objects_view")
        self.objects_view.setSelectionMode(QListView.SingleSelection)
        self.objects_view.setDragEnabled(True)
        self.objects_view.setDragDropMode(QListView.DragOnly)
        self.objects_view.setMovement(QListView.Snap)
        self.objects_view.setViewMode(QListView.ListMode)
        self.objects_view_frame.layout().insertWidget(1, self.objects_view)

    def setupUi(self, SceneDefinitionWindow):
        SceneDefinitionWindow.setObjectName("SceneDefinitionWindow")
        SceneDefinitionWindow.resize(1543, 939)
        self.centralWidget = QtWidgets.QWidget(SceneDefinitionWindow)
        self.centralWidget.setObjectName("centralWidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.centralWidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setSpacing(6)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.frame_1 = QtWidgets.QFrame(self.centralWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(10)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame_1.sizePolicy().hasHeightForWidth())
        self.frame_1.setSizePolicy(sizePolicy)
        self.frame_1.setMaximumSize(QtCore.QSize(200, 16777215))
        self.frame_1.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_1.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_1.setObjectName("frame_1")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.frame_1)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.label_2 = QtWidgets.QLabel(self.frame_1)
        self.label_2.setObjectName("label_2")
        self.verticalLayout_2.addWidget(self.label_2)
        self.scenes_list = QtWidgets.QListView(self.frame_1)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(10)
        sizePolicy.setHeightForWidth(self.scenes_list.sizePolicy().hasHeightForWidth())
        self.scenes_list.setSizePolicy(sizePolicy)
        self.scenes_list.setObjectName("scenes_list")
        self.verticalLayout_2.addWidget(self.scenes_list)
        self.frame = QtWidgets.QFrame(self.frame_1)
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout(self.frame)
        self.horizontalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_5.setSpacing(6)
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_5.addItem(spacerItem)
        self.scene_up_btn = QtWidgets.QToolButton(self.frame)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("isar/ui/images/up_button.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.scene_up_btn.setIcon(icon)
        self.scene_up_btn.setObjectName("scene_up_btn")
        self.horizontalLayout_5.addWidget(self.scene_up_btn)
        self.scene_down_btn = QtWidgets.QToolButton(self.frame)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap("isar/ui/images/down_button.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.scene_down_btn.setIcon(icon1)
        self.scene_down_btn.setObjectName("scene_down_btn")
        self.horizontalLayout_5.addWidget(self.scene_down_btn)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_5.addItem(spacerItem1)
        self.verticalLayout_2.addWidget(self.frame)
        self.new_scene_btn = QtWidgets.QPushButton(self.frame_1)
        self.new_scene_btn.setObjectName("new_scene_btn")
        self.verticalLayout_2.addWidget(self.new_scene_btn)
        self.clone_scene_btn = QtWidgets.QPushButton(self.frame_1)
        self.clone_scene_btn.setObjectName("clone_scene_btn")
        self.verticalLayout_2.addWidget(self.clone_scene_btn)
        self.delete_scene_btn = QtWidgets.QPushButton(self.frame_1)
        self.delete_scene_btn.setObjectName("delete_scene_btn")
        self.verticalLayout_2.addWidget(self.delete_scene_btn)
        self.init_scene_size_btn = QtWidgets.QPushButton(self.frame_1)
        self.init_scene_size_btn.setObjectName("init_scene_size_btn")
        self.verticalLayout_2.addWidget(self.init_scene_size_btn)
        self.define_navigation_flow_btn = QtWidgets.QPushButton(self.frame_1)
        self.define_navigation_flow_btn.setObjectName("define_navigation_flow_btn")
        self.verticalLayout_2.addWidget(self.define_navigation_flow_btn)
        self.ev_act_rules_btn = QtWidgets.QPushButton(self.frame_1)
        self.ev_act_rules_btn.setObjectName("ev_act_rules_btn")
        self.verticalLayout_2.addWidget(self.ev_act_rules_btn)
        self.line = QtWidgets.QFrame(self.frame_1)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.line.sizePolicy().hasHeightForWidth())
        self.line.setSizePolicy(sizePolicy)
        self.line.setMinimumSize(QtCore.QSize(0, 20))
        self.line.setLineWidth(10)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.verticalLayout_2.addWidget(self.line)
        self.project_name_le = QtWidgets.QLineEdit(self.frame_1)
        self.project_name_le.setObjectName("project_name_le")
        self.verticalLayout_2.addWidget(self.project_name_le)
        self.create_proj_btn = QtWidgets.QPushButton(self.frame_1)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.create_proj_btn.setFont(font)
        self.create_proj_btn.setObjectName("create_proj_btn")
        self.verticalLayout_2.addWidget(self.create_proj_btn)
        self.save_proj_btn = QtWidgets.QPushButton(self.frame_1)
        self.save_proj_btn.setObjectName("save_proj_btn")
        self.verticalLayout_2.addWidget(self.save_proj_btn)
        self.load_proj_btn = QtWidgets.QPushButton(self.frame_1)
        self.load_proj_btn.setObjectName("load_proj_btn")
        self.verticalLayout_2.addWidget(self.load_proj_btn)
        self.horizontalLayout.addWidget(self.frame_1)
        self.frame_2 = QtWidgets.QFrame(self.centralWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(90)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame_2.sizePolicy().hasHeightForWidth())
        self.frame_2.setSizePolicy(sizePolicy)
        self.frame_2.setMinimumSize(QtCore.QSize(800, 0))
        self.frame_2.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_2.setObjectName("frame_2")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.frame_2)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.frame_3 = QtWidgets.QFrame(self.frame_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(5)
        sizePolicy.setHeightForWidth(self.frame_3.sizePolicy().hasHeightForWidth())
        self.frame_3.setSizePolicy(sizePolicy)
        self.frame_3.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_3.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_3.setObjectName("frame_3")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.frame_3)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setSpacing(6)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.camers_view_frame = QtWidgets.QFrame(self.frame_3)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(60)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.camers_view_frame.sizePolicy().hasHeightForWidth())
        self.camers_view_frame.setSizePolicy(sizePolicy)
        self.camers_view_frame.setMinimumSize(QtCore.QSize(250, 250))
        self.camers_view_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.camers_view_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.camers_view_frame.setObjectName("camers_view_frame")
        self.verticalLayout_6 = QtWidgets.QVBoxLayout(self.camers_view_frame)
        self.verticalLayout_6.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_6.setSpacing(6)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.camera_view_container = QtWidgets.QFrame(self.camers_view_frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.camera_view_container.sizePolicy().hasHeightForWidth())
        self.camera_view_container.setSizePolicy(sizePolicy)
        self.camera_view_container.setStyleSheet("background-color: rgb(205, 255, 250);")
        self.camera_view_container.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.camera_view_container.setFrameShadow(QtWidgets.QFrame.Raised)
        self.camera_view_container.setObjectName("camera_view_container")
        self.verticalLayout_6.addWidget(self.camera_view_container)
        self.camera_view_toolbox = QtWidgets.QFrame(self.camers_view_frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.camera_view_toolbox.sizePolicy().hasHeightForWidth())
        self.camera_view_toolbox.setSizePolicy(sizePolicy)
        self.camera_view_toolbox.setMaximumSize(QtCore.QSize(16777215, 40))
        self.camera_view_toolbox.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.camera_view_toolbox.setFrameShadow(QtWidgets.QFrame.Raised)
        self.camera_view_toolbox.setObjectName("camera_view_toolbox")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.camera_view_toolbox)
        self.horizontalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_4.setSpacing(6)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.select_btn = QtWidgets.QToolButton(self.camera_view_toolbox)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap("isar/ui/images/select.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.select_btn.setIcon(icon2)
        self.select_btn.setCheckable(True)
        self.select_btn.setAutoExclusive(False)
        self.select_btn.setObjectName("select_btn")
        self.annotation_buttons = QtWidgets.QButtonGroup(SceneDefinitionWindow)
        self.annotation_buttons.setObjectName("annotation_buttons")
        self.annotation_buttons.addButton(self.select_btn)
        self.horizontalLayout_4.addWidget(self.select_btn)
        self.delete_btn = QtWidgets.QToolButton(self.camera_view_toolbox)
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap("isar/ui/images/delete.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.delete_btn.setIcon(icon3)
        self.delete_btn.setObjectName("delete_btn")
        self.horizontalLayout_4.addWidget(self.delete_btn)
        self.undo_btn = QtWidgets.QToolButton(self.camera_view_toolbox)
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap("isar/ui/images/undo.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.undo_btn.setIcon(icon4)
        self.undo_btn.setObjectName("undo_btn")
        self.horizontalLayout_4.addWidget(self.undo_btn)
        self.redo_btn = QtWidgets.QToolButton(self.camera_view_toolbox)
        icon5 = QtGui.QIcon()
        icon5.addPixmap(QtGui.QPixmap("isar/ui/images/redo.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.redo_btn.setIcon(icon5)
        self.redo_btn.setObjectName("redo_btn")
        self.horizontalLayout_4.addWidget(self.redo_btn)
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem2)
        self.mouse_object_position_label = QtWidgets.QLabel(self.camera_view_toolbox)
        self.mouse_object_position_label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.mouse_object_position_label.setObjectName("mouse_object_position_label")
        self.horizontalLayout_4.addWidget(self.mouse_object_position_label)
        self.mouse_image_position_label = QtWidgets.QLabel(self.camera_view_toolbox)
        self.mouse_image_position_label.setMinimumSize(QtCore.QSize(100, 0))
        self.mouse_image_position_label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.mouse_image_position_label.setObjectName("mouse_image_position_label")
        self.horizontalLayout_4.addWidget(self.mouse_image_position_label)
        self.verticalLayout_6.addWidget(self.camera_view_toolbox)
        self.horizontalLayout_2.addWidget(self.camers_view_frame)
        self.splitter = QtWidgets.QSplitter(self.frame_3)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(40)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.splitter.sizePolicy().hasHeightForWidth())
        self.splitter.setSizePolicy(sizePolicy)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setHandleWidth(5)
        self.splitter.setChildrenCollapsible(False)
        self.splitter.setObjectName("splitter")
        self.objects_view_frame = QtWidgets.QFrame(self.splitter)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(30)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.objects_view_frame.sizePolicy().hasHeightForWidth())
        self.objects_view_frame.setSizePolicy(sizePolicy)
        self.objects_view_frame.setMaximumSize(QtCore.QSize(200, 16777215))
        self.objects_view_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.objects_view_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.objects_view_frame.setObjectName("objects_view_frame")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.objects_view_frame)
        self.verticalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_4.setSpacing(6)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.label_3 = QtWidgets.QLabel(self.objects_view_frame)
        self.label_3.setObjectName("label_3")
        self.verticalLayout_4.addWidget(self.label_3)
        self.track_objects_checkbox = QtWidgets.QCheckBox(self.objects_view_frame)
        self.track_objects_checkbox.setObjectName("track_objects_checkbox")
        self.verticalLayout_4.addWidget(self.track_objects_checkbox)
        self.label_5 = QtWidgets.QLabel(self.objects_view_frame)
        self.label_5.setObjectName("label_5")
        self.verticalLayout_4.addWidget(self.label_5)
        self.annotations_list = QtWidgets.QListView(self.objects_view_frame)
        self.annotations_list.setObjectName("annotations_list")
        self.verticalLayout_4.addWidget(self.annotations_list)
        self.properties_view_frame = QtWidgets.QFrame(self.splitter)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(70)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.properties_view_frame.sizePolicy().hasHeightForWidth())
        self.properties_view_frame.setSizePolicy(sizePolicy)
        self.properties_view_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.properties_view_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.properties_view_frame.setObjectName("properties_view_frame")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.properties_view_frame)
        self.verticalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_5.setSpacing(6)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.label_4 = QtWidgets.QLabel(self.properties_view_frame)
        self.label_4.setObjectName("label_4")
        self.verticalLayout_5.addWidget(self.label_4)
        self.properties_view = QtWidgets.QTableView(self.properties_view_frame)
        self.properties_view.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.properties_view.setObjectName("properties_view")
        self.properties_view.horizontalHeader().setMinimumSectionSize(5)
        self.properties_view.verticalHeader().setMinimumSectionSize(5)
        self.verticalLayout_5.addWidget(self.properties_view)
        self.horizontalLayout_2.addWidget(self.splitter)
        self.verticalLayout.addWidget(self.frame_3)
        self.annotations_frame = QtWidgets.QFrame(self.frame_2)
        self.annotations_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.annotations_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.annotations_frame.setObjectName("annotations_frame")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.annotations_frame)
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_3.setSpacing(0)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.label = QtWidgets.QLabel(self.annotations_frame)
        self.label.setObjectName("label")
        self.verticalLayout_3.addWidget(self.label)
        self.frame_4 = QtWidgets.QFrame(self.annotations_frame)
        self.frame_4.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_4.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_4.setObjectName("frame_4")
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout(self.frame_4)
        self.horizontalLayout_6.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_6.setSpacing(0)
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setSpacing(6)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.text_btn = QtWidgets.QToolButton(self.frame_4)
        icon6 = QtGui.QIcon()
        icon6.addPixmap(QtGui.QPixmap("isar/ui/images/text.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.text_btn.setIcon(icon6)
        self.text_btn.setCheckable(True)
        self.text_btn.setAutoExclusive(True)
        self.text_btn.setAutoRaise(False)
        self.text_btn.setObjectName("text_btn")
        self.annotation_buttons.addButton(self.text_btn)
        self.horizontalLayout_3.addWidget(self.text_btn)
        self.audio_btn = QtWidgets.QToolButton(self.frame_4)
        icon7 = QtGui.QIcon()
        icon7.addPixmap(QtGui.QPixmap("isar/ui/images/audio.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.audio_btn.setIcon(icon7)
        self.audio_btn.setCheckable(True)
        self.audio_btn.setAutoExclusive(True)
        self.audio_btn.setObjectName("audio_btn")
        self.annotation_buttons.addButton(self.audio_btn)
        self.horizontalLayout_3.addWidget(self.audio_btn)
        self.arrow_btn = QtWidgets.QToolButton(self.frame_4)
        icon8 = QtGui.QIcon()
        icon8.addPixmap(QtGui.QPixmap("isar/ui/images/arrow.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.arrow_btn.setIcon(icon8)
        self.arrow_btn.setCheckable(True)
        self.arrow_btn.setAutoExclusive(True)
        self.arrow_btn.setObjectName("arrow_btn")
        self.annotation_buttons.addButton(self.arrow_btn)
        self.horizontalLayout_3.addWidget(self.arrow_btn)
        self.check_box_btn = QtWidgets.QToolButton(self.frame_4)
        icon9 = QtGui.QIcon()
        icon9.addPixmap(QtGui.QPixmap("isar/ui/images/check_box.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.check_box_btn.setIcon(icon9)
        self.check_box_btn.setCheckable(True)
        self.check_box_btn.setAutoExclusive(True)
        self.check_box_btn.setObjectName("check_box_btn")
        self.annotation_buttons.addButton(self.check_box_btn)
        self.horizontalLayout_3.addWidget(self.check_box_btn)
        self.video_btn = QtWidgets.QToolButton(self.frame_4)
        icon10 = QtGui.QIcon()
        icon10.addPixmap(QtGui.QPixmap("isar/ui/images/video.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.video_btn.setIcon(icon10)
        self.video_btn.setCheckable(True)
        self.video_btn.setAutoExclusive(True)
        self.video_btn.setObjectName("video_btn")
        self.annotation_buttons.addButton(self.video_btn)
        self.horizontalLayout_3.addWidget(self.video_btn)
        self.relationship_btn = QtWidgets.QToolButton(self.frame_4)
        icon11 = QtGui.QIcon()
        icon11.addPixmap(QtGui.QPixmap("isar/ui/images/relationship.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.relationship_btn.setIcon(icon11)
        self.relationship_btn.setCheckable(True)
        self.relationship_btn.setAutoExclusive(True)
        self.relationship_btn.setObjectName("relationship_btn")
        self.annotation_buttons.addButton(self.relationship_btn)
        self.horizontalLayout_3.addWidget(self.relationship_btn)
        self.timer_btn = QtWidgets.QToolButton(self.frame_4)
        icon12 = QtGui.QIcon()
        icon12.addPixmap(QtGui.QPixmap("isar/ui/images/timer.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.timer_btn.setIcon(icon12)
        self.timer_btn.setCheckable(True)
        self.timer_btn.setAutoExclusive(True)
        self.timer_btn.setObjectName("timer_btn")
        self.annotation_buttons.addButton(self.timer_btn)
        self.horizontalLayout_3.addWidget(self.timer_btn)
        self.image_btn = QtWidgets.QToolButton(self.frame_4)
        icon13 = QtGui.QIcon()
        icon13.addPixmap(QtGui.QPixmap("isar/ui/images/image.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.image_btn.setIcon(icon13)
        self.image_btn.setCheckable(True)
        self.image_btn.setAutoExclusive(True)
        self.image_btn.setObjectName("image_btn")
        self.annotation_buttons.addButton(self.image_btn)
        self.horizontalLayout_3.addWidget(self.image_btn)
        self.rectangle_btn = QtWidgets.QToolButton(self.frame_4)
        icon14 = QtGui.QIcon()
        icon14.addPixmap(QtGui.QPixmap("isar/ui/images/rectangle.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.rectangle_btn.setIcon(icon14)
        self.rectangle_btn.setCheckable(True)
        self.rectangle_btn.setAutoExclusive(True)
        self.rectangle_btn.setObjectName("rectangle_btn")
        self.annotation_buttons.addButton(self.rectangle_btn)
        self.horizontalLayout_3.addWidget(self.rectangle_btn)
        self.line_btn = QtWidgets.QToolButton(self.frame_4)
        icon15 = QtGui.QIcon()
        icon15.addPixmap(QtGui.QPixmap("isar/ui/images/line.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.line_btn.setIcon(icon15)
        self.line_btn.setCheckable(True)
        self.line_btn.setAutoExclusive(True)
        self.line_btn.setObjectName("line_btn")
        self.annotation_buttons.addButton(self.line_btn)
        self.horizontalLayout_3.addWidget(self.line_btn)
        self.circle_btn = QtWidgets.QToolButton(self.frame_4)
        icon16 = QtGui.QIcon()
        icon16.addPixmap(QtGui.QPixmap("isar/ui/images/circle.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.circle_btn.setIcon(icon16)
        self.circle_btn.setCheckable(True)
        self.circle_btn.setAutoExclusive(True)
        self.circle_btn.setObjectName("circle_btn")
        self.annotation_buttons.addButton(self.circle_btn)
        self.horizontalLayout_3.addWidget(self.circle_btn)
        self.action_button_btn = QtWidgets.QToolButton(self.frame_4)
        icon17 = QtGui.QIcon()
        icon17.addPixmap(QtGui.QPixmap("isar/ui/images/action_button.jpg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.action_button_btn.setIcon(icon17)
        self.action_button_btn.setCheckable(True)
        self.action_button_btn.setAutoExclusive(True)
        self.action_button_btn.setObjectName("action_button_btn")
        self.annotation_buttons.addButton(self.action_button_btn)
        self.horizontalLayout_3.addWidget(self.action_button_btn)
        self.curve_btn = QtWidgets.QToolButton(self.frame_4)
        icon18 = QtGui.QIcon()
        icon18.addPixmap(QtGui.QPixmap("isar/ui/images/curve_line.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.curve_btn.setIcon(icon18)
        self.curve_btn.setCheckable(True)
        self.curve_btn.setAutoExclusive(True)
        self.curve_btn.setObjectName("curve_btn")
        self.annotation_buttons.addButton(self.curve_btn)
        self.horizontalLayout_3.addWidget(self.curve_btn)
        self.animation_btn = QtWidgets.QToolButton(self.frame_4)
        icon19 = QtGui.QIcon()
        icon19.addPixmap(QtGui.QPixmap("isar/ui/images/animation.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.animation_btn.setIcon(icon19)
        self.animation_btn.setCheckable(True)
        self.animation_btn.setAutoExclusive(True)
        self.animation_btn.setObjectName("animation_btn")
        self.annotation_buttons.addButton(self.animation_btn)
        self.horizontalLayout_3.addWidget(self.animation_btn)
        self.feedback_btn = QtWidgets.QToolButton(self.frame_4)
        icon20 = QtGui.QIcon()
        icon20.addPixmap(QtGui.QPixmap("isar/ui/images/feedback.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.feedback_btn.setIcon(icon20)
        self.feedback_btn.setCheckable(True)
        self.feedback_btn.setAutoExclusive(True)
        self.feedback_btn.setObjectName("feedback_btn")
        self.annotation_buttons.addButton(self.feedback_btn)
        self.horizontalLayout_3.addWidget(self.feedback_btn)
        self.object_area_btn = QtWidgets.QToolButton(self.frame_4)
        icon21 = QtGui.QIcon()
        icon21.addPixmap(QtGui.QPixmap("isar/ui/images/object_area.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.object_area_btn.setIcon(icon21)
        self.object_area_btn.setCheckable(True)
        self.object_area_btn.setAutoExclusive(True)
        self.object_area_btn.setObjectName("object_area_btn")
        self.annotation_buttons.addButton(self.object_area_btn)
        self.horizontalLayout_3.addWidget(self.object_area_btn)
        self.counter_btn = QtWidgets.QToolButton(self.frame_4)
        icon22 = QtGui.QIcon()
        icon22.addPixmap(QtGui.QPixmap("isar/ui/images/counter.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.counter_btn.setIcon(icon22)
        self.counter_btn.setCheckable(True)
        self.counter_btn.setAutoExclusive(True)
        self.counter_btn.setObjectName("counter_btn")
        self.annotation_buttons.addButton(self.counter_btn)
        self.horizontalLayout_3.addWidget(self.counter_btn)
        spacerItem3 = QtWidgets.QSpacerItem(638, 17, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem3)
        self.horizontalLayout_6.addLayout(self.horizontalLayout_3)
        self.verticalLayout_3.addWidget(self.frame_4)
        self.verticalLayout.addWidget(self.annotations_frame)
        self.horizontalLayout.addWidget(self.frame_2)
        SceneDefinitionWindow.setCentralWidget(self.centralWidget)
        self.menuBar = QtWidgets.QMenuBar(SceneDefinitionWindow)
        self.menuBar.setGeometry(QtCore.QRect(0, 0, 1543, 17))
        self.menuBar.setObjectName("menuBar")
        self.menuFile = QtWidgets.QMenu(self.menuBar)
        self.menuFile.setObjectName("menuFile")
        SceneDefinitionWindow.setMenuBar(self.menuBar)
        self.mainToolBar = QtWidgets.QToolBar(SceneDefinitionWindow)
        self.mainToolBar.setObjectName("mainToolBar")
        SceneDefinitionWindow.addToolBar(QtCore.Qt.TopToolBarArea, self.mainToolBar)
        self.statusBar = QtWidgets.QStatusBar(SceneDefinitionWindow)
        self.statusBar.setObjectName("statusBar")
        SceneDefinitionWindow.setStatusBar(self.statusBar)
        self.actionCreate_Project = QtWidgets.QAction(SceneDefinitionWindow)
        self.actionCreate_Project.setObjectName("actionCreate_Project")
        self.actionLoad_Project = QtWidgets.QAction(SceneDefinitionWindow)
        self.actionLoad_Project.setObjectName("actionLoad_Project")
        self.actionSave_Project = QtWidgets.QAction(SceneDefinitionWindow)
        self.actionSave_Project.setObjectName("actionSave_Project")
        self.actionEvents = QtWidgets.QAction(SceneDefinitionWindow)
        self.actionEvents.setObjectName("actionEvents")
        self.actionActions = QtWidgets.QAction(SceneDefinitionWindow)
        self.actionActions.setObjectName("actionActions")
        self.actionRules = QtWidgets.QAction(SceneDefinitionWindow)
        self.actionRules.setObjectName("actionRules")
        self.menuFile.addAction(self.actionLoad_Project)
        self.menuBar.addAction(self.menuFile.menuAction())

        self.retranslateUi(SceneDefinitionWindow)
        QtCore.QMetaObject.connectSlotsByName(SceneDefinitionWindow)

    def retranslateUi(self, SceneDefinitionWindow):
        _translate = QtCore.QCoreApplication.translate
        SceneDefinitionWindow.setWindowTitle(_translate("SceneDefinitionWindow", "SceneDefinitionWindow"))
        self.label_2.setText(_translate("SceneDefinitionWindow", "Scenes"))
        self.scene_up_btn.setText(_translate("SceneDefinitionWindow", "..."))
        self.scene_down_btn.setText(_translate("SceneDefinitionWindow", "..."))
        self.new_scene_btn.setText(_translate("SceneDefinitionWindow", "New Scene"))
        self.clone_scene_btn.setText(_translate("SceneDefinitionWindow", "Clone"))
        self.delete_scene_btn.setText(_translate("SceneDefinitionWindow", "Delete"))
        self.init_scene_size_btn.setText(_translate("SceneDefinitionWindow", "Init Scn Size"))
        self.define_navigation_flow_btn.setText(_translate("SceneDefinitionWindow", "Nav. Flow ..."))
        self.ev_act_rules_btn.setText(_translate("SceneDefinitionWindow", "Ev., Act., Rules ..."))
        self.project_name_le.setText(_translate("SceneDefinitionWindow", "[project_name]"))
        self.create_proj_btn.setText(_translate("SceneDefinitionWindow", "CreateProject..."))
        self.save_proj_btn.setText(_translate("SceneDefinitionWindow", "Save..."))
        self.load_proj_btn.setText(_translate("SceneDefinitionWindow", "Load..."))
        self.select_btn.setText(_translate("SceneDefinitionWindow", "..."))
        self.delete_btn.setText(_translate("SceneDefinitionWindow", "..."))
        self.undo_btn.setText(_translate("SceneDefinitionWindow", "..."))
        self.redo_btn.setText(_translate("SceneDefinitionWindow", "..."))
        self.mouse_object_position_label.setText(_translate("SceneDefinitionWindow", "mouse object position"))
        self.mouse_image_position_label.setText(_translate("SceneDefinitionWindow", "mouse image position"))
        self.label_3.setText(_translate("SceneDefinitionWindow", "Physical Objects"))
        self.track_objects_checkbox.setText(_translate("SceneDefinitionWindow", "Track Objects"))
        self.label_5.setText(_translate("SceneDefinitionWindow", "Annotations"))
        self.label_4.setText(_translate("SceneDefinitionWindow", "Properties"))
        self.label.setText(_translate("SceneDefinitionWindow", "Annotation Tools"))
        self.text_btn.setText(_translate("SceneDefinitionWindow", "..."))
        self.arrow_btn.setText(_translate("SceneDefinitionWindow", "..."))
        self.check_box_btn.setText(_translate("SceneDefinitionWindow", "..."))
        self.video_btn.setText(_translate("SceneDefinitionWindow", "..."))
        self.relationship_btn.setText(_translate("SceneDefinitionWindow", "..."))
        self.timer_btn.setText(_translate("SceneDefinitionWindow", "..."))
        self.image_btn.setText(_translate("SceneDefinitionWindow", "..."))
        self.rectangle_btn.setText(_translate("SceneDefinitionWindow", "..."))
        self.line_btn.setText(_translate("SceneDefinitionWindow", "..."))
        self.circle_btn.setText(_translate("SceneDefinitionWindow", "..."))
        self.action_button_btn.setText(_translate("SceneDefinitionWindow", "..."))
        self.curve_btn.setText(_translate("SceneDefinitionWindow", "..."))
        self.animation_btn.setText(_translate("SceneDefinitionWindow", "..."))
        self.feedback_btn.setText(_translate("SceneDefinitionWindow", "..."))
        self.object_area_btn.setText(_translate("SceneDefinitionWindow", "..."))
        self.counter_btn.setText(_translate("SceneDefinitionWindow", "..."))
        self.menuFile.setTitle(_translate("SceneDefinitionWindow", "File"))
        self.actionCreate_Project.setText(_translate("SceneDefinitionWindow", "Create Project ..."))
        self.actionLoad_Project.setText(_translate("SceneDefinitionWindow", "Load Project ..."))
        self.actionSave_Project.setText(_translate("SceneDefinitionWindow", "Save Project ..."))
        self.actionEvents.setText(_translate("SceneDefinitionWindow", "Events ..."))
        self.actionActions.setText(_translate("SceneDefinitionWindow", "Actions ..."))
        self.actionRules.setText(_translate("SceneDefinitionWindow", "Rules ..."))

    def setup_signals(self):
        # scenes list
        self.scene_up_btn.clicked.connect(self.scene_up_btn_clicked)
        self.scene_down_btn.clicked.connect(self.scene_down_btn_clicked)

        self.new_scene_btn.clicked.connect(self.new_scene_btn_clicked)
        self.clone_scene_btn.clicked.connect(self.clone_scene_btn_clicked)
        self.delete_scene_btn.clicked.connect(self.delete_scene_btn_clicked)
        self.define_navigation_flow_btn.clicked.connect(self.define_navigation_btn_clicked)
        self.ev_act_rules_btn.clicked.connect(self.ev_act_rules_btn_clicked)

        self.scenes_list.selectionModel().currentChanged.connect(self.sceneslist_current_changed)

        self.delete_btn.clicked.connect(self.delete_btn_clicked)

        self.init_scene_size_btn.clicked.connect(self.initialize_scene_size)

        self.save_proj_btn.clicked.connect(self.save_project_btn_clicked)
        self.load_proj_btn.clicked.connect(self.load_project_btn_clicked)
        self.create_proj_btn.clicked.connect(self.create_project_btn_clicked)

        # annotation buttons
        for btn in self.annotation_buttons.buttons():
            btn.clicked.connect(functools.partial(self.annotation_btn_clicked, btn))

        self.annotations_list.selectionModel().currentChanged.connect(self.annotationslist_current_changed)
        self.annotations_list.selectionModel().selectionChanged.connect(self.annotationslist_current_changed)

        self.track_objects_checkbox.stateChanged.connect(self.toggle_object_tracking)

    def sceneslist_current_changed(self):
        current_index = self.scenes_list.selectionModel().currentIndex()
        self.scenes_list.selectionModel().select(current_index, QItemSelectionModel.Select)

        scenes_model = self.scenes_list.model()
        scenes_model.set_current_scene(current_index)

    @staticmethod
    def project_loaded():
        servicemanager.on_project_loaded()

    def current_scene_changed(self):
        scenes_model = self.scenes_list.model()
        current_index = scenes_model.find_index(scenes_model.get_current_scene())
        self.scenes_list.setCurrentIndex(current_index)

        self.annotations_list.model().set_scene(scenes_model.get_current_scene())
        self.camera_view.set_annotations_model(self.annotations_list.model())

        self.objects_view.model().set_scene(scenes_model.get_current_scene())
        self.camera_view.set_physical_objects_model(self.objects_view.model())

        servicemanager.current_scene_changed(self.scenes_model.get_current_scene())

        self.camera_view.set_active_annotation_tool(self.select_btn.objectName())
        self.select_btn.setChecked(True)
        if self.annotation_buttons.checkedButton():
            btn = self.annotation_buttons.checkedButton()
            btn.setChecked(False)
            select_btn = self.annotation_buttons.button(SceneDefinitionWindow.SELECT_BTN_ID)
            if select_btn:
                select_btn.setChecked(True)

        if self.annotations_list.model().rowCount() > 0:
            first_item = self.annotations_list.model().createIndex(0, 0)
            self.annotations_list.selectionModel().select(first_item, QItemSelectionModel.Select)
            self.annotations_list.selectionModel().setCurrentIndex(first_item, QItemSelectionModel.Current)
        else:
            self.annotationslist_current_changed()

    def annotationslist_current_changed(self):
        current_index = self.annotations_list.selectionModel().currentIndex()
        annotationsmodel = self.annotations_list.model()
        annotationsmodel.set_current_annotation(current_index)
        self.properties_view.model().set_annotation(annotationsmodel.current_annotation)
        self.properties_view.resizeRowsToContents()

    def delete_btn_clicked(self):
        focus_widget = self.focusWidget().objectName()
        if focus_widget == "objects_view":
            # delete the selected physical object from the scene (if it is included in the scene)
            # if the object has annotations, they are also deleted
            phys_obj_model: PhysicalObjectsModel = self.objects_view.model()
            current_index = self.objects_view.selectionModel().currentIndex()
            phys_obj: PhysicalObject = phys_obj_model.get_physical_object_at(current_index)
            phys_obj_model.delete_physical_object_from_scene(phys_obj)
            annotations_model: AnnotationsModel = self.annotations_list.model()
            annotations_model.update_view()

        elif focus_widget == "annotations_list":
            annotations_model: AnnotationsModel = self.annotations_list.model()
            current_index = self.annotations_list.selectionModel().currentIndex()
            annotations_model.delete_annotation_at(current_index)
            self.properties_view.model().set_annotation(None)

    def save_project_btn_clicked(self):
        logger.info("Save project")
        parent_dir = None
        project_name = None
        if not scenemodel.current_project:
            parent_dir = QFileDialog.getExistingDirectory()
            if parent_dir is None or parent_dir == "":
                return
            project_name = self.project_name_le.text()

        scenes_model = self.scenes_list.model()
        new_project_created = scenes_model.save_project(parent_dir, project_name)
        if new_project_created:
            self.setWindowTitle(scenemodel.current_project.name)
            # self.project_name_le.setReadOnly(True)
            self.project_name_le.setEnabled(False)
            self.create_proj_btn.setEnabled(False)

    def create_project_btn_clicked(self):
        logger.info("Create project")
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        parent_dir = QFileDialog.getExistingDirectory(options=options)
        if parent_dir is None or parent_dir == "":
            return
        project_name = self.project_name_le.text()
        result = scenemodel.create_project(parent_dir, project_name)
        if not result:
            QMessageBox.warning(None, "Error", "Creating project failed!")
        else:
            self.setWindowTitle(scenemodel.current_project.name)
            # self.project_name_le.setReadOnly(True)
            self.project_name_le.setEnabled(False)
            self.create_proj_btn.setEnabled(False)

    def load_project_btn_clicked(self):
        logger.info("Load project")
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        project_filename = QFileDialog.getOpenFileName(parent=None, filter="(*.json)", options=options)[0]
        project_dir = os.path.dirname(project_filename)
        project_name = os.path.splitext(os.path.basename(project_filename))[0]
        if project_dir is None or project_dir == "":
            return
        self.project_name_le.setText(project_name)
        scenes_model = self.scenes_list.model()
        scenes_model.load_project(project_dir, project_name)
        index = self.scenes_list.model().index(0, 0)
        self.scenes_list.setCurrentIndex(index)

    def annotation_btn_clicked(self, btn):
        if btn.isChecked():
            btn.setAutoExclusive(False)
        else:
            btn.setAutoExclusive(True)

        self.camera_view.set_active_annotation_tool(btn.objectName())

    def new_scene_btn_clicked(self):
        selected_index = self.scenes_list.selectionModel().currentIndex()
        self.scenes_list.model().new_scene(selected_index)

    def clone_scene_btn_clicked(self):
        selected_index = self.scenes_list.selectionModel().currentIndex()
        self.scenes_list.model().clone_scene(selected_index)

    def delete_scene_btn_clicked(self):
        # TODO: show confirm dialog. cannot be undone. then call delete scene on scene model
        selected_index = self.scenes_list.selectionModel().currentIndex()
        if selected_index.row() == self.scenes_list.model().rowCount(None) - 1:
            # it was the last scene in view, update the selection to previous one
            new_selection = self.scenes_list.model().createIndex(selected_index.row() - 1, 0)
            self.scenes_list.selectionModel().select(new_selection, QItemSelectionModel.Select)
            self.scenes_list.selectionModel().setCurrentIndex(new_selection, QItemSelectionModel.Current)

        self.scenes_list.model().delete_scene(selected_index)

    def define_navigation_btn_clicked(self):
        scenes_model = self.scenes_list.model()
        ordered_scene_ids = scenes_model.get_ordered_scene_ids()
        input_text = ""
        for scene_id in ordered_scene_ids:
            input_text = input_text + scene_id + "\n"

        navigation_text, ok_pressed = QInputDialog.getMultiLineText(None,
                                                            "Define scene navigation flow",
                                                            "Scene navigation flow:",
                                                            input_text)
        if ok_pressed:
            scene_ids = navigation_text.strip().split("\n")
            for scene_id in scene_ids:
                if scene_id not in ordered_scene_ids:
                    QMessageBox.warning(None, "Error", "One or more of the scene ids is incorrect. \n" +
                                        "Maybe you changed the id when changing the order or ids. \n" +
                                        "Try again.")
                    
                    return

            scenes_model.set_scene_navigation_flow(scene_ids)

    def scene_up_btn_clicked(self):
        selected_index = self.scenes_list.selectionModel().currentIndex()
        self.scenes_list.model().move_scene_up(selected_index)

    def scene_down_btn_clicked(self):
        selected_index = self.scenes_list.selectionModel().currentIndex()
        self.scenes_list.model().move_scene_down(selected_index)

    def ev_act_rules_btn_clicked(self):
        ev_act_rules_dialog = EventsActionsRulesDialog(self.scenes_model,
                                                       self.annotations_model,
                                                       self.physical_objects_model,
                                                       self)
        ev_act_rules_dialog.setModal(True)
        ev_act_rules_dialog.show()

    def setup_camera_service(self):
        self._camera_service = servicemanager.get_service(ServiceNames.CAMERA1)
        self._camera_service.start_capture()

    def setup_object_detection_service(self):
        self._object_detection_service = servicemanager.get_service(ServiceNames.OBJECT_DETECTION)
        self._selection_stick_service = servicemanager.get_service(ServiceNames.SELECTION_STICK)
        self._hand_tracking_service = servicemanager.get_service(ServiceNames.HAND_TRACKING_SERVICE)

    def setup_timer(self):
        self._camera_view_timer = QTimer()
        self._camera_view_timer.timeout.connect(self.update_camera_view)
        self._camera_view_timer.start(isar.CAMERA_UPDATE_INTERVAL)

        t = Thread(target=self.run_object_detection)
        t.daemon = True
        t.start()

    def setup_models(self):
        self.scenes_model = ScenesModel()
        self.scenes_list.setModel(self.scenes_model)
        current_scene = self.scenes_list.model().get_current_scene()
        self.scenes_model.scene_changed.connect(self.current_scene_changed)
        self.scenes_model.project_loaded.connect(self.project_loaded)

        self.physical_objects_model = PhysicalObjectsModel()
        self.physical_objects_model.set_scene(current_scene)
        all_physical_obj = []
        for po_s in self._object_detection_service.get_physical_objects().values():
            all_physical_obj.extend(po_s)
        self.physical_objects_model.set_all_physical_objects(all_physical_obj)
        self.camera_view.set_physical_objects_model(self.physical_objects_model)
        self.objects_view.setModel(self.physical_objects_model)

        self.annotations_model = AnnotationsModel()
        self.annotations_model.set_scene(current_scene)

        self.camera_view.set_annotations_model(self.annotations_model)
        self.annotations_list.setModel(self.annotations_model)

        self._selection_stick_service.set_physical_objects_model(self.physical_objects_model)
        self._selection_stick_service.set_annotations_model(self.annotations_model)

        self._hand_tracking_service.set_physical_objects_model(self.physical_objects_model)
        self._hand_tracking_service.set_annotations_model(self.annotations_model)

        selection_service = servicemanager.get_service(ServiceNames.SELECTION_SERVICE)
        selection_service.annotations_model = self.annotations_model

        actions_service = servicemanager.get_service(ServiceNames.ACTIONS_SERVICE)
        actions_service.set_annotations_model(self.annotations_model)
        actions_service.set_scenes_model(self.scenes_model)

        object_tracking_service = servicemanager.get_service(ServiceNames.OBJECT_TRACKING_SERVICE)
        object_tracking_service.set_annotations_model(self.annotations_model)
        object_tracking_service.set_scenes_model(self.scenes_model)
        object_tracking_service.set_physical_objects_model(self.physical_objects_model)

        checkbox_service = servicemanager.get_service(ServiceNames.CHECKBOX_SERVICE)
        checkbox_service.set_annotations_model(self.annotations_model)
        checkbox_service.set_scenes_model(self.scenes_model)

        rules_service = servicemanager.get_service(ServiceNames.RULES_SERVICE)
        rules_service.set_scenes_model(self.scenes_model)

        properties_model = AnnotationPropertiesModel()
        self.properties_view.setModel(properties_model)
        annotation_property_item_delegate = AnnotationPropertyItemDelegate()
        annotation_property_item_delegate.phys_obj_model = self.physical_objects_model
        self.properties_view.setItemDelegate(annotation_property_item_delegate)

    def update_camera_view(self):
        camera_frame = self._camera_service.get_frame()

        if camera_frame is None:
            # logger.error("camera_frame is None")
            return

        if not self.scene_size_initialized:
            logger.warning("Scene size is not initialized.")

        self.camera_view.set_camera_frame(camera_frame)

    def toggle_object_tracking(self):
        if self.track_objects_checkbox.isChecked():
            isar.OBJECT_TRACKING_ACTIVE = True
        else:
            isar.OBJECT_TRACKING_ACTIVE = False

    def run_object_detection(self):
        while True:
            time.sleep(isar.OBJECT_DETECTION_INTERVAL)
            if isar.OBJECT_TRACKING_ACTIVE:
                camera_frame = self._camera_service.get_frame()
                if camera_frame == isar.POISON_PILL:
                    logger.info(
                        "Object detection thread in scene definition window got poison pill from camera. Break.")
                    break

                self._object_detection_service.start_object_detection()
                scene_phys_objs_names = self.physical_objects_model.get_scene_physical_objects_names()
                if scene_phys_objs_names is not None and len(scene_phys_objs_names) > 0:
                    self._object_detection_service.get_present_objects(camera_frame,
                                                                       scene_phys_objs_names,
                                                                       callback=self.on_obj_detection_complete)
            else:
                self._object_detection_service.stop_object_detection()
                self.physical_objects_model.update_present_physical_objects(None)

    def on_obj_detection_complete(self, phys_obj_predictions):
        self.physical_objects_model.update_present_physical_objects(phys_obj_predictions)

    def initialize_scene_size(self):
        max_iter = 100
        num_iter = -1
        while True:
            num_iter += 1
            camera_frame = self._camera_service.get_frame()
            if camera_frame is None:
                # logger.error("camera_frame is None")
                continue

            # compute scene rect in projector-space
            scene_rect_c, _, _ = sceneutil.compute_scene_rect(camera_frame)
            if scene_rect_c is None and num_iter < max_iter:
                continue
            elif scene_rect_c is not None:
                self.scene_rect = scene_rect_c
                self.scene_size = (self.scene_rect[2], self.scene_rect[3])
                self.scene_scale_factor_c = sceneutil.get_scene_scale_factor_c(
                    camera_frame.raw_image.shape, scene_rect_c)
                self.scene_size_initialized = True

                sceneutil.scene_rect_c = scene_rect_c
                sceneutil.scene_scale_factor_c = self.scene_scale_factor_c

                if self.scenes_model is not None:
                    self.scenes_model.scene_size = self.scene_size

                logger.info("Scene size initialized successfully!")
                break
            else:
                logger.warning("Could not initialize the scene size.")
                break

    def reset_scene_size(self):
        # TODO: Experimental. Remove in production code. Also remove the button.
        self.scene_rect = None
        self.scene_size = None
        self.scene_size_initialized = False

    def get_camera_view_scale_factor(self):
        if self.scene_size is not None:
            width_scale = self.camera_view.geometry().width() / self.scene_size[0]
            height_scale = self.camera_view.geometry().height() / self.scene_size[1]
            return width_scale, height_scale
        else:
            return None

    def get_scene_scale_factor(self, scene_rect):
        cam_capture_size = self._camera_service.get_camera_capture_size()
        width_scale_factor = scene_rect[2] / cam_capture_size[0]
        height_scale_factor = scene_rect[3] / cam_capture_size[1]
        return width_scale_factor, height_scale_factor

    def update_mouse_position_label(self, position, obj_name=None):
        if obj_name is None and position is not None:
            self.mouse_image_position_label.setText("Image:" + str(position))
        elif obj_name is not None and position is not None:
            self.mouse_object_position_label.setText(obj_name + ":" + str(position))
        else:
            self.mouse_object_position_label.setText("")


class PhysicalObjectsView(QListView):

    DRAG_START_DISTANCE = 10

    def __init__(self, main_window):
        super().__init__()
        self.drag_start_position = None
        self.selected_po = None
        self.main_window = main_window

    def mousePressEvent(self, event: QMouseEvent):
        self.drag_start_position = event.pos()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        if not (event.buttons() & Qt.LeftButton):
            return

        if (event.pos() - self.drag_start_position).manhattanLength() < \
                PhysicalObjectsView.DRAG_START_DISTANCE:
            return

        selected_indices = self.selectedIndexes()
        mime_data = self.model().mimeData(selected_indices)
        # If the phys object is already on the scene, we cannot drop it again.
        # The model return a None as mime_data.
        if not mime_data:
            return

        drag = QDrag(self)
        drag.setMimeData(mime_data)
        if self.selected_po is not None:
            pixmap: QPixmap = sceneutil.get_pixmap_from_np_image(self.selected_po.template_image)
            scale_factor = self.main_window.get_camera_view_scale_factor()
            width = scale_factor[0] * pixmap.width()
            height = scale_factor[1] * pixmap.height()
            drag.setPixmap(pixmap.scaled(width, height))

        drop_action = drag.exec(Qt.CopyAction)

    def selectionChanged(self, selected: QItemSelection, deselected: QItemSelection):
        if selected is None:
            return

        if selected.indexes() is None or len(selected.indexes()) == 0:
            return

        self.selected_po = self.model().get_physical_object_at(selected.indexes()[0])




