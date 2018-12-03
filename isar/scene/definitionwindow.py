import logging

from PyQt5 import uic
from PyQt5.QtCore import QTimer, QItemSelectionModel
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QDialog, QWidget, QGridLayout, QHBoxLayout

from isar.camera.camera import CameraService
from isar.scene import model
from isar.scene.cameraview import CameraView
from isar.services import servicemanager
from isar.services.servicemanager import ServiceNames


logger = logging.getLogger("isar.scene")


class SceneDefinitionWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.camera_view = None
        self.setup_ui()

        self._camera_service: CameraService = None
        self.setup_camera_service()

        self._timer = None
        self.setup_timer()

        # self.setAttribute(QtCore.Qt.WA_QuitOnClose, True)
        self.setup_models()

        self.setup_signals()

    def setup_ui(self):
        uic.loadUi("isar/ui/scene_definition.ui", self)
        self.camera_view_container.setLayout(QHBoxLayout())
        self.camera_view = CameraView(self.camera_view_container)
        self.camera_view_container.layout().setContentsMargins(0, 0, 0, 0)
        self.camera_view_container.layout().addWidget(self.camera_view, stretch=1)

    def setup_signals(self):
        self.new_scene_btn.clicked.connect(self.new_scene_btn_clicked)
        self.clone_scene_btn.clicked.connect(self.clone_scene_btn_clicked)
        self.delete_scene_btn.clicked.connect(self.delete_scene_btn_clicked)
        self.scenes_list.selectionModel().currentChanged.connect(self.scenes_list_current_changed)

    def scenes_list_current_changed(self):
        selected_index = self.scenes_list.selectionModel().currentIndex()
        self.scenes_list.selectionModel().select(selected_index, QItemSelectionModel.Select)
        self.scenes_list.model().set_current_scene(selected_index)
        self.camera_view.scene = self.scenes_list.model().current_scene

    def new_scene_btn_clicked(self):
        selected_index = self.scenes_list.selectionModel().currentIndex()
        self.scenes_list.model().new_scene(selected_index)

        # new_selection = self.scenes_list.model().createIndex(selected_index.row() + 1, 0)
        # self.scenes_list.selectionModel().select(new_selection, QItemSelectionModel.Select)
        # self.scenes_list.selectionModel().setCurrentIndex(new_selection, QItemSelectionModel.Current)

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

    def setup_camera_service(self):
        self._camera_service = servicemanager.get_service(ServiceNames.CAMERA1)
        self._camera_service.start_capture()

    def setup_timer(self):
        self._timer = QTimer()
        self._timer.timeout.connect(self.update_camera_view)
        self._timer.start(5)

    def setup_models(self):
        scenes_model = model.create_dummy_scenes_model()
        self.scenes_list.setModel(scenes_model)



        self.camera_view.scene = self.scenes_list.selectionModel().currentIndex()

    def update_camera_view(self):
        camera_frame = self._camera_service.get_frame(flipped=True)
        self.camera_view.set_camera_frame(camera_frame)

    def closeEvent(self, QCloseEvent):
        self._timer.stop()
        self._camera_service.stop_capture()


