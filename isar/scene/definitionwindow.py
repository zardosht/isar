import functools
import logging

from PyQt5 import uic
from PyQt5.QtCore import QTimer, QItemSelectionModel, QEvent, QObject, Qt, QItemSelection
from PyQt5.QtGui import QImage, QPixmap, QDragMoveEvent, QMouseEvent, QDrag
from PyQt5.QtWidgets import QDialog, QWidget, QGridLayout, QHBoxLayout, QToolButton, QListView

from isar.camera.camera import CameraService
from isar.scene import util
from isar.scene.annotationmodel import AnnotationsModel
from isar.scene.annotationpropertymodel import AnnotationPropertiesModel
from isar.scene.cameraview import CameraView
from isar.scene.physicalobjectmodel import PhysicalObjectsModel
from isar.scene.scenemodel import ScenesModel
from isar.services import servicemanager
from isar.services.servicemanager import ServiceNames


logger = logging.getLogger("isar.definitionwindow")


class SceneDefinitionWindow(QDialog):

    SELECT_BTN_ID = 10

    def __init__(self):
        super().__init__()
        self.camera_view = None
        self.objects_view = None
        self.setup_ui()

        self._camera_service: CameraService = None
        self.setup_camera_service()

        self._object_detection_service = None
        self.setup_object_detection_service()

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

        self.annotation_buttons.setId(self.select_btn, SceneDefinitionWindow.SELECT_BTN_ID)
        self.select_btn.setChecked(True)

        self.objects_view = PhysicalObjectsView(self)
        self.objects_view.setSelectionMode(QListView.SingleSelection)
        self.objects_view.setDragEnabled(True)
        self.objects_view.setDragDropMode(QListView.DragOnly)
        self.objects_view.setMovement(QListView.Snap)
        self.objects_view.setViewMode(QListView.ListMode)
        self.objects_view_frame.layout().insertWidget(1, self.objects_view)

    def setup_signals(self):
        # scenes list
        self.new_scene_btn.clicked.connect(self.new_scene_btn_clicked)
        self.clone_scene_btn.clicked.connect(self.clone_scene_btn_clicked)
        self.delete_scene_btn.clicked.connect(self.delete_scene_btn_clicked)
        self.scenes_list.selectionModel().currentChanged.connect(self.sceneslist_current_changed)
        self.scenes_list.selectionModel().selectionChanged.connect(self.sceneslist_current_changed)

        # annotation buttons
        for btn in self.annotation_buttons.buttons():
            btn.clicked.connect(functools.partial(self.annotation_btn_clicked, btn))

        self.annotations_list.selectionModel().currentChanged.connect(self.annotationslist_current_changed)
        self.annotations_list.selectionModel().selectionChanged.connect(self.annotationslist_current_changed)

    def sceneslist_current_changed(self):
        current_index = self.scenes_list.selectionModel().currentIndex()
        self.scenes_list.selectionModel().select(current_index, QItemSelectionModel.Select)

        scenes_model = self.scenes_list.model()
        scenes_model.set_current_scene(current_index)

        self.annotations_list.model().set_scene(scenes_model.current_scene)
        self.camera_view.annotations_model = self.annotations_list.model()

        self.objects_view.model().set_scene(scenes_model.current_scene)
        self.camera_view.physical_objects_model = self.objects_view.model()

        self.camera_view.set_active_annotation_tool(None)
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

    def annotation_btn_clicked(self, btn):
        if btn.isChecked():
            btn.setAutoExclusive(False)
        else:
            btn.setAutoExclusive(True)

        self.camera_view.set_active_annotation_tool(btn.objectName())

    def new_scene_btn_clicked(self):
        selected_index = self.scenes_list.selectionModel().currentIndex()
        self.scenes_list.model().new_scene(selected_index)
        self.sceneslist_current_changed()

    def clone_scene_btn_clicked(self):
        selected_index = self.scenes_list.selectionModel().currentIndex()
        self.scenes_list.model().clone_scene(selected_index)
        self.sceneslist_current_changed()

    def delete_scene_btn_clicked(self):
        # TODO: show confirm dialog. cannot be undone. then call delete scene on scene model
        selected_index = self.scenes_list.selectionModel().currentIndex()
        if selected_index.row() == self.scenes_list.model().rowCount(None) - 1:
            # it was the last scene in view, update the selection to previous one
            new_selection = self.scenes_list.model().createIndex(selected_index.row() - 1, 0)
            self.scenes_list.selectionModel().select(new_selection, QItemSelectionModel.Select)
            self.scenes_list.selectionModel().setCurrentIndex(new_selection, QItemSelectionModel.Current)

        self.scenes_list.model().delete_scene(selected_index)
        self.sceneslist_current_changed()

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
        scenes_model = ScenesModel()
        self.scenes_list.setModel(scenes_model)
        current_scene = self.scenes_list.model().current_scene

        physical_objects_model = PhysicalObjectsModel()
        physical_objects_model.set_scene(current_scene)
        all_physical_obj = []
        for po_s in self._object_detection_service.get_physical_objects().values():
            all_physical_obj.extend(po_s)
        physical_objects_model.set_all_physical_objects(all_physical_obj)
        self.camera_view.physical_objects_model = physical_objects_model
        self.objects_view.setModel(physical_objects_model)

        annotations_model = AnnotationsModel()
        annotations_model.set_scene(current_scene)
        self.camera_view.annotations_model = annotations_model
        self.annotations_list.setModel(annotations_model)

        properties_model = AnnotationPropertiesModel()
        self.properties_view.setModel(properties_model)

    def update_camera_view(self):
        camera_frame = self._camera_service.get_frame(flipped=True)

        # TODO:
        #  * give the camera frame to object detection servcie
        #  * get the list of present physical objects and
        #  * update the PhysicalObjectsModel's __present_physical_objects list

        # TODO:
        #  * later in camera view, draw bounding boxes for all the present_phys_objs instead of their images.

        self.camera_view.set_camera_frame(camera_frame)

    def closeEvent(self, QCloseEvent):
        self._timer.stop()
        self._camera_service.stop_capture()

    def get_scale_factor(self):
        capture_size = self._camera_service.get_camera_capture_size()
        if capture_size is not None:
            width_scale = self.camera_view.geometry().width() / capture_size[0]
            height_scale = self.camera_view.geometry().height() / capture_size[1]
            return width_scale, height_scale
        else:
            return None


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
        drag = QDrag(self)
        drag.setMimeData(mime_data)
        if self.selected_po is not None:
            pixmap: QPixmap = util.get_pixmap_from_np_image(self.selected_po.image)
            scale_factor = self.main_window.get_scale_factor()
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




