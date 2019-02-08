import logging

from PyQt5 import QtWidgets, QtCore, uic
from PyQt5.QtCore import QItemSelectionModel, QTimer
from PyQt5.QtWidgets import QHBoxLayout, QFileDialog, QWidget

from isar.camera.camera import CameraService
from isar.scene.annotationmodel import AnnotationsModel
from isar.scene.cameraview import CameraView
from isar.scene.physicalobjectmodel import PhysicalObjectsModel
from isar.scene.scenemodel import ScenesModel
from isar.services import servicemanager
from isar.services.servicemanager import ServiceNames

logger = logging.getLogger("isar.domainlearning")


class DomainLearningWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.camera_view = None
        self.objects_view = None
        self.setup_ui()

        self._camera_service: CameraService = None
        self.setup_camera_service()

        self._object_detection_service = None
        self.setup_object_detection_service()

        self.setAttribute(QtCore.Qt.WA_QuitOnClose, True)

        self.scenes_model = None
        self.physical_objects_model = None
        self.annotations_model = None
        self.setup_models()

        self.setup_signals()

        self._timer = None
        self.setup_timer()

    def setup_ui(self):
        uic.loadUi("isar/ui/domain_learning.ui", self)
        self.camera_view_container.setLayout(QHBoxLayout())
        self.camera_view = CameraView(self.camera_view_container, None)
        self.camera_view_container.layout().setContentsMargins(0, 0, 0, 0)
        self.camera_view_container.layout().addWidget(self.camera_view, stretch=1)

    def setup_signals(self):
        # scenes list
        self.calibrate_btn.clicked.connect(self.calibrate_projector)
        self.load_proj_btn.clicked.connect(self.load_project_btn_clicked)

    def calibrate_projector(self):
        pass

    def load_project_btn_clicked(self):
        logger.info("Load project")
        project_dir = QFileDialog.getExistingDirectory()
        if project_dir is None or project_dir == "":
            return
        project_name = self.project_name_le.text()
        scenes_model = self.scenes_list.model()
        scenes_model.load_project(project_dir, project_name)
        index = self.scenes_list.model().index(0, 0)
        self.scenes_list.selectionModel().select(index, QItemSelectionModel.Select)

    def setup_camera_service(self):
        self._camera_service = servicemanager.get_service(ServiceNames.CAMERA1)
        self._camera_service.start_capture()

    def setup_object_detection_service(self):
        self._object_detection_service = servicemanager.get_service(ServiceNames.OBJECT_DETECTION)

    def setup_timer(self):
        self._timer = QTimer()
        self._timer.timeout.connect(self.update_camera_view)
        self._timer.start(5)

    def setup_models(self):
        self.scenes_model = ScenesModel()
        self.scenes_list.setModel(self.scenes_model)
        current_scene = self.scenes_list.model().current_scene

        self.physical_objects_model = PhysicalObjectsModel()
        self.physical_objects_model.set_scene(current_scene)
        all_physical_obj = []
        for po_s in self._object_detection_service.get_physical_objects().values():
            all_physical_obj.extend(po_s)
        self.physical_objects_model.set_all_physical_objects(all_physical_obj)
        self.camera_view.physical_objects_model = self.physical_objects_model
        # self.objects_view.setModel(physical_objects_model)

        self.annotations_model = AnnotationsModel()
        self.annotations_model.set_scene(current_scene)
        self.camera_view.annotations_model = self.annotations_model
        # self.annotations_list.setModel(annotations_model)

    def update_camera_view(self):
        camera_frame = self._camera_service.get_frame(flipped_y=True)
        if camera_frame is None:
            # logger.error("camera_frame is None")
            return

        self.camera_view.set_camera_frame(camera_frame)

        # phys_obj_model: PhysicalObjectsModel = self.objects_view.model()
        if self.track_objects_checkbox.isChecked():
            scene_phys_objs_names =  self.physical_objects_model.get_scene_physical_objects_names()
            if scene_phys_objs_names is not None and len(scene_phys_objs_names) > 0:
                self._object_detection_service.get_present_objects(camera_frame,
                                                                   scene_phys_objs_names,
                                                                   callback=self.on_obj_detection_complete)
        else:
            self.physical_objects_model.update_present_physical_objects(None)

    def on_obj_detection_complete(self, phys_obj_predictions):
        phys_obj_model: PhysicalObjectsModel = self.objects_view.model()
        phys_obj_model.update_present_physical_objects(phys_obj_predictions)




