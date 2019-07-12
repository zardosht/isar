import logging
import os
import time
from threading import Thread

from PyQt5 import QtCore, uic, QtWidgets
from PyQt5.QtCore import QItemSelectionModel, QTimer, Qt
from PyQt5.QtWidgets import QFileDialog, QMainWindow

import isar
from isar.camera.camera import CameraService
from isar.projection.projector import ProjectorView
from isar.scene.annotationmodel import AnnotationsModel
from isar.scene.physicalobjectmodel import PhysicalObjectsModel
from isar.scene.scenemodel import ScenesModel
from isar.services import servicemanager
from isar.services.servicemanager import ServiceNames


logger = logging.getLogger("isar.domainlearning")


class DomainLearningWindow(QMainWindow):
    def __init__(self, screen_id):
        super().__init__()
        self.objects_view = None
        self.setupUi(self)
        self.projector_view = None

        self._camera_service: CameraService = None
        self.setup_camera_service()

        self.projector_initialized = self.setup_projector_view(screen_id)
        if not self.projector_initialized:
            logger.error("Projector is not ready! Return")
            return

        self._object_detection_service = None
        self._selection_stick_service = None
        self._hand_tracking_service = None
        self.setup_object_detection_service()

        self.setAttribute(QtCore.Qt.WA_QuitOnClose, True)

        self.scenes_model = None
        self.physical_objects_model = None
        self.annotations_model = None
        self.setup_models()

        self.setup_signals()

        self._projector_view_timer = None
        self._object_detection_timer = None
        self.setup_timers()

    def setupUi(self, DomainLearningWindow):
        DomainLearningWindow.setObjectName("DomainLearningWindow")
        DomainLearningWindow.resize(971, 800)
        self.centralWidget = QtWidgets.QWidget(DomainLearningWindow)
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
        self.verticalLayout_2.setSpacing(6)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.label_2 = QtWidgets.QLabel(self.frame_1)
        self.label_2.setObjectName("label_2")
        self.verticalLayout_2.addWidget(self.label_2)
        self.scenes_list = QtWidgets.QListView(self.frame_1)
        self.scenes_list.setObjectName("scenes_list")
        self.verticalLayout_2.addWidget(self.scenes_list)
        self.track_objects_checkbox = QtWidgets.QCheckBox(self.frame_1)
        self.track_objects_checkbox.setObjectName("track_objects_checkbox")
        self.verticalLayout_2.addWidget(self.track_objects_checkbox)
        self.calibrate_btn = QtWidgets.QPushButton(self.frame_1)
        self.calibrate_btn.setMinimumSize(QtCore.QSize(0, 0))
        self.calibrate_btn.setObjectName("calibrate_btn")
        self.verticalLayout_2.addWidget(self.calibrate_btn)
        self.init_scene_size_btn = QtWidgets.QPushButton(self.frame_1)
        self.init_scene_size_btn.setObjectName("init_scene_size_btn")
        self.verticalLayout_2.addWidget(self.init_scene_size_btn)
        self.line = QtWidgets.QFrame(self.frame_1)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.verticalLayout_2.addWidget(self.line)
        self.project_name_le = QtWidgets.QLineEdit(self.frame_1)
        self.project_name_le.setObjectName("project_name_le")
        self.verticalLayout_2.addWidget(self.project_name_le)
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
        self.verticalLayout.setSpacing(6)
        self.verticalLayout.setObjectName("verticalLayout")
        self.instructions_label = QtWidgets.QLabel(self.frame_2)
        self.instructions_label.setWordWrap(True)
        self.instructions_label.setObjectName("instructions_label")
        self.verticalLayout.addWidget(self.instructions_label)
        self.horizontalLayout.addWidget(self.frame_2)
        DomainLearningWindow.setCentralWidget(self.centralWidget)
        self.menuBar = QtWidgets.QMenuBar(DomainLearningWindow)
        self.menuBar.setGeometry(QtCore.QRect(0, 0, 971, 22))
        self.menuBar.setObjectName("menuBar")
        self.menuFile = QtWidgets.QMenu(self.menuBar)
        self.menuFile.setObjectName("menuFile")
        self.menuEvents_and_Actions = QtWidgets.QMenu(self.menuBar)
        self.menuEvents_and_Actions.setObjectName("menuEvents_and_Actions")
        DomainLearningWindow.setMenuBar(self.menuBar)
        self.mainToolBar = QtWidgets.QToolBar(DomainLearningWindow)
        self.mainToolBar.setObjectName("mainToolBar")
        DomainLearningWindow.addToolBar(QtCore.Qt.TopToolBarArea, self.mainToolBar)
        self.statusBar = QtWidgets.QStatusBar(DomainLearningWindow)
        self.statusBar.setObjectName("statusBar")
        DomainLearningWindow.setStatusBar(self.statusBar)
        self.actionCreate_Project = QtWidgets.QAction(DomainLearningWindow)
        self.actionCreate_Project.setObjectName("actionCreate_Project")
        self.actionLoad_Project = QtWidgets.QAction(DomainLearningWindow)
        self.actionLoad_Project.setObjectName("actionLoad_Project")
        self.actionSave_Project = QtWidgets.QAction(DomainLearningWindow)
        self.actionSave_Project.setObjectName("actionSave_Project")
        self.actionEvents = QtWidgets.QAction(DomainLearningWindow)
        self.actionEvents.setObjectName("actionEvents")
        self.actionActions = QtWidgets.QAction(DomainLearningWindow)
        self.actionActions.setObjectName("actionActions")
        self.actionRules = QtWidgets.QAction(DomainLearningWindow)
        self.actionRules.setObjectName("actionRules")
        self.menuFile.addAction(self.actionCreate_Project)
        self.menuFile.addAction(self.actionLoad_Project)
        self.menuFile.addAction(self.actionSave_Project)
        self.menuEvents_and_Actions.addAction(self.actionEvents)
        self.menuEvents_and_Actions.addAction(self.actionActions)
        self.menuEvents_and_Actions.addAction(self.actionRules)
        self.menuBar.addAction(self.menuFile.menuAction())
        self.menuBar.addAction(self.menuEvents_and_Actions.menuAction())

        self.retranslateUi(DomainLearningWindow)
        QtCore.QMetaObject.connectSlotsByName(DomainLearningWindow)

    def retranslateUi(self, DomainLearningWindow):
        _translate = QtCore.QCoreApplication.translate
        DomainLearningWindow.setWindowTitle(_translate("DomainLearningWindow", "DomainLearningWindow"))
        self.label_2.setText(_translate("DomainLearningWindow", "Scenes"))
        self.track_objects_checkbox.setText(_translate("DomainLearningWindow", "Track Objects"))
        self.calibrate_btn.setText(_translate("DomainLearningWindow", "Calibrate Projector"))
        self.init_scene_size_btn.setText(_translate("DomainLearningWindow", "Init Scene Size"))
        self.project_name_le.setText(_translate("DomainLearningWindow", "[project_name]"))
        self.load_proj_btn.setText(_translate("DomainLearningWindow", "Load..."))
        self.instructions_label.setText(_translate("DomainLearningWindow", "Instructions ... / Status ... "))
        self.menuFile.setTitle(_translate("DomainLearningWindow", "File"))
        self.menuEvents_and_Actions.setTitle(_translate("DomainLearningWindow", "Events and Actions"))
        self.actionCreate_Project.setText(_translate("DomainLearningWindow", "Create Project ..."))
        self.actionLoad_Project.setText(_translate("DomainLearningWindow", "Load Project ..."))
        self.actionSave_Project.setText(_translate("DomainLearningWindow", "Save Project ..."))
        self.actionEvents.setText(_translate("DomainLearningWindow", "Events ..."))
        self.actionActions.setText(_translate("DomainLearningWindow", "Actions ..."))
        self.actionRules.setText(_translate("DomainLearningWindow", "Rules ..."))

    def setup_projector_view(self, screen_id):
        self.projector_view = ProjectorView(self.projector_view, screen_id, self._camera_service)
        if self.projector_view.is_projector_ready():
            self.projector_view.setWindowFlag(Qt.Window)
            self.calibrate_projector()
            return True
        else:
            logger.error("Could not initialize projector. Make sure projector is connected and is turned on!")
            return False

    def setup_signals(self):
        # scenes list
        self.calibrate_btn.clicked.connect(self.calibrate_projector)
        self.init_scene_size_btn.clicked.connect(self.init_scene_size)
        self.load_proj_btn.clicked.connect(self.load_project_btn_clicked)
        self.scenes_list.selectionModel().currentChanged.connect(self.sceneslist_current_changed)

    def calibrate_projector(self):
        self.projector_view.calibrating = True
        self.projector_view.calibrate_projector()

    def init_scene_size(self):
        self.projector_view.init_scene_size()

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

    def setup_camera_service(self):
        self._camera_service = servicemanager.get_service(ServiceNames.CAMERA1)
        self._camera_service.start_capture()

    def setup_object_detection_service(self):
        self._object_detection_service = servicemanager.get_service(ServiceNames.OBJECT_DETECTION)
        self._selection_stick_service = servicemanager.get_service(ServiceNames.SELECTION_STICK)
        self._hand_tracking_service = servicemanager.get_service(ServiceNames.HAND_TRACKING_SERVICE)

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
        self.projector_view.set_physical_objects_model(self.physical_objects_model)
        # self.objects_view.setModel(physical_objects_model)

        self.annotations_model = AnnotationsModel()
        self.annotations_model.set_scene(current_scene)
        self.projector_view.set_physical_objects_model(self.physical_objects_model)

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

        # self.annotations_list.setModel(annotations_model)

    def sceneslist_current_changed(self):
        current_index = self.scenes_list.selectionModel().currentIndex()
        self.scenes_list.selectionModel().select(current_index, QItemSelectionModel.Select)

        scenes_model = self.scenes_list.model()
        scenes_model.set_current_scene(current_index)

    @staticmethod
    def project_loaded():
        servicemanager.on_project_loaded()

    def current_scene_changed(self):
        current_index = self.scenes_model.find_index(self.scenes_model.get_current_scene())
        self.scenes_list.setCurrentIndex(current_index)

        self.annotations_model.set_scene(self.scenes_model.get_current_scene())
        self.physical_objects_model.set_scene(self.scenes_model.get_current_scene())
        self.projector_view.set_annotations_model(self.annotations_model)

        servicemanager.current_scene_changed(self.scenes_model.get_current_scene())

    def setup_timers(self):
        self._projector_view_timer = QTimer()
        self._projector_view_timer.timeout.connect(self.update_projector_view)
        self._projector_view_timer.start(isar.CAMERA_UPDATE_INTERVAL)

        t = Thread(target=self.run_object_detection)
        t.daemon = True
        t.start()

    def update_projector_view(self):
        if self.projector_view.calibrating:
            return
        else:
            camera_frame = self._camera_service.get_frame()
            if camera_frame is None:
                return

            self.projector_view.update_projector_view(camera_frame)

    def run_object_detection(self):
        while True:
            time.sleep(isar.OBJECT_DETECTION_INTERVAL)
            if self.track_objects_checkbox.isChecked():
                camera_frame = self._camera_service.get_frame()
                if camera_frame == isar.POISON_PILL:
                    logger.info(
                        "Object detection thread in domain learning window got poison pill from camera. Break.")
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

    def close(self):
        self._projector_view_timer.stop()
        self.projector_view.close()
        super().close()

    # Just to get the other window (the projector widget) to close :/
    def closeEvent(self, event):
        self.projector_view.close()
        super().closeEvent(event)



