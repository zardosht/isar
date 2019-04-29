import logging
import os
import time

from PyQt5 import QtCore, uic
from PyQt5.QtCore import QItemSelectionModel, QTimer, Qt
from PyQt5.QtWidgets import QHBoxLayout, QFileDialog, QWidget, QMainWindow
from isar.camera.camera import CameraService
from isar.projection.projector import ProjectorView
from isar.scene.annotationmodel import AnnotationsModel
from isar.scene.cameraview import CameraView
from isar.scene.physicalobjectmodel import PhysicalObjectsModel
from isar.scene.scenemodel import ScenesModel
from isar.services import servicemanager
from isar.services.servicemanager import ServiceNames


logger = logging.getLogger("isar.domainlearning")


class DomainLearningWindow(QWidget):
    def __init__(self, screen_id):
        super().__init__()
        self.camera_view = None
        self.objects_view = None
        self.setup_ui()
        self.projector_view = None

        self._camera_service: CameraService = None
        self.setup_camera_service()

        self.setup_projector_view(screen_id)

        self._object_detection_service = None
        self._selection_stick_service = None
        self.setup_object_detection_service()

        self.setAttribute(QtCore.Qt.WA_QuitOnClose, True)

        self.scenes_model = None
        self.physical_objects_model = None
        self.annotations_model = None
        self.setup_models()

        self.setup_signals()

        # self._camera_view_timer = None
        self._cam_view_update_thread = None
        self._projector_view_timer = None
        self.setup_timers()

    def setup_ui(self):
        uic.loadUi("isar/ui/domain_learning.ui", self)
        self.camera_view_container.setLayout(QHBoxLayout())
        self.camera_view = CameraView(self.camera_view_container, None)
        self.camera_view_container.layout().setContentsMargins(0, 0, 0, 0)
        self.camera_view_container.layout().addWidget(self.camera_view, stretch=1)

    def setup_projector_view(self, screen_id):
        self.projector_view = ProjectorView(self.projector_view, screen_id, self._camera_service)
        self.projector_view.setWindowFlag(Qt.Window)
        self.calibrate_projector()

    def setup_signals(self):
        # scenes list
        self.calibrate_btn.clicked.connect(self.calibrate_projector)
        self.init_scene_size_btn.clicked.connect(self.init_scene_size)
        self.load_proj_btn.clicked.connect(self.load_project_btn_clicked)
        self.scenes_list.selectionModel().currentChanged.connect(self.sceneslist_current_changed)
        self.scenes_list.selectionModel().selectionChanged.connect(self.sceneslist_current_changed)

    def calibrate_projector(self):
        self.projector_view.calibrating = True
        self.projector_view.calibrate_projector()

    def init_scene_size(self):
        self.projector_view.init_scene_size()

    def load_project_btn_clicked(self):
        logger.info("Load project")
        project_filename = QFileDialog.getOpenFileName(filter="(*.json)")[0]
        project_dir = os.path.dirname(project_filename)
        project_name = os.path.splitext(os.path.basename(project_filename))[0]
        if project_dir is None or project_dir == "":
            return
        self.project_name_le.setText(project_name)
        scenes_model = self.scenes_list.model()
        scenes_model.load_project(project_dir, project_name)
        index = self.scenes_list.model().index(0, 0)
        self.scenes_list.selectionModel().select(index, QItemSelectionModel.Select)

    def setup_camera_service(self):
        self._camera_service = servicemanager.get_service(ServiceNames.CAMERA1)
        self._camera_service.start_capture()

    def setup_object_detection_service(self):
        self._object_detection_service = servicemanager.get_service(ServiceNames.OBJECT_DETECTION)
        self._selection_stick_service = servicemanager.get_service(ServiceNames.SELECTION_STICK)

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
        self.camera_view.set_physical_objects_model(self.physical_objects_model)
        self.projector_view.set_physical_objects_model(self.physical_objects_model)
        # self.objects_view.setModel(physical_objects_model)

        self.annotations_model = AnnotationsModel()
        self.annotations_model.set_scene(current_scene)
        self.camera_view.set_annotations_model(self.annotations_model)
        self.projector_view.set_physical_objects_model(self.physical_objects_model)

        self._selection_stick_service.set_physical_objects_model(self.physical_objects_model)
        self._selection_stick_service.set_annotations_model(self.annotations_model)

        # self.annotations_list.setModel(annotations_model)

    def sceneslist_current_changed(self):
        current_index = self.scenes_list.selectionModel().currentIndex()
        self.scenes_list.selectionModel().select(current_index, QItemSelectionModel.Select)

        scenes_model = self.scenes_list.model()
        scenes_model.set_current_scene(current_index)

        self.annotations_model.set_scene(scenes_model.current_scene)
        self.physical_objects_model.set_scene(scenes_model.current_scene)
        self.camera_view.set_annotations_model(self.annotations_model)
        self.projector_view.set_annotations_model(self.annotations_model)

        # self.objects_view.model().set_scene(scenes_model.current_scene)
        # self.camera_view.set_physical_objects_model(self.objects_view.model())

    def setup_timers(self):
        self._cam_view_update_thread = CameraViewUpdateThread(self._camera_service)
        # self._cam_view_update_thread.camera_frame_fetched.connect(self.update_camera_view)
        # self._cam_view_update_thread.start(5)

        self._projector_view_timer = QTimer()
        self._projector_view_timer.timeout.connect(self.update_projector_view)
        self._projector_view_timer.start(5)

    def update_camera_view(self, camera_frame):
        if camera_frame is None:
            # logger.error("camera_frame is None")
            return

        self.camera_view.set_camera_frame(camera_frame)

        # phys_obj_model: PhysicalObjectsModel = self.objects_view.model()
        if self.track_objects_checkbox.isChecked():
            scene_phys_objs_names = self.physical_objects_model.get_scene_physical_objects_names()
            if scene_phys_objs_names is not None and len(scene_phys_objs_names) > 0:
                self._object_detection_service.get_present_objects(camera_frame,
                                                                   scene_phys_objs_names,
                                                                   callback=self.on_obj_detection_complete)
        else:
            self.physical_objects_model.update_present_physical_objects(None)

    def update_projector_view(self):
        if self.projector_view.calibrating:
            return
        else:
            camera_frame = self._camera_service.get_frame()
            self._selection_stick_service.camera_img = camera_frame.raw_image
            self.projector_view.update_projector_view(camera_frame)

        if self.track_objects_checkbox.isChecked():
            scene_phys_objs_names = self.physical_objects_model.get_scene_physical_objects_names()
            if scene_phys_objs_names is not None and len(scene_phys_objs_names) > 0:
                self._object_detection_service.get_present_objects(camera_frame,
                                                                   scene_phys_objs_names,
                                                                   callback=self.on_obj_detection_complete)
        else:
            self.physical_objects_model.update_present_physical_objects(None)

    def on_obj_detection_complete(self, phys_obj_predictions):
        self.physical_objects_model.update_present_physical_objects(phys_obj_predictions)

    def close(self):
        self._projector_view_timer.stop()
        self._cam_view_update_thread.stop()
        self.projector_view.close()
        super().close()


class CameraViewUpdateThread(QtCore.QThread):
    camera_frame_fetched = QtCore.pyqtSignal(object)

    def __init__(self, camera_service):
        super().__init__()
        self.camera_service = camera_service
        self._stop = False

    def run(self):
        while not self._stop:
            camera_frame = self.camera_service.get_frame(flipped_y=True)
            if camera_frame is None:
                # logger.error("camera_frame is None")
                continue

            self.camera_frame_fetched.emit(camera_frame)
            time.sleep(0.005)

    def stop(self):
        self._stop = True


# Just to get the other window (the projector widget) to close :/
class DomainLearningMainWindow(QMainWindow):

    def closeEvent(self, event):
        self.centralWidget().close()
        super(DomainLearningMainWindow, self).closeEvent(event)

