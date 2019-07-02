import functools
import logging
import os

from PyQt5 import uic, QtCore
from PyQt5.QtCore import QTimer, QItemSelectionModel, Qt, QItemSelection
from PyQt5.QtGui import QPixmap, QMouseEvent, QDrag
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QListView, QFileDialog, QMessageBox, QInputDialog, QMainWindow

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

        self._timer = None
        self.setup_timer()

    def setup_ui(self):
        uic.loadUi("isar/ui/scene_definition.ui", self)
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
        parent_dir = QFileDialog.getExistingDirectory()
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
        project_filename = QFileDialog.getOpenFileName(filter="(*.json)")[0]
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
        self._timer = QTimer()
        self._timer.timeout.connect(self.update_camera_view)
        self._timer.start(5)

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
        # camera_frame = self._camera_service.get_frame(flipped_y=True)
        camera_frame = self._camera_service.get_frame()

        if camera_frame is None:
            # logger.error("camera_frame is None")
            return

        if not self.scene_size_initialized:
            logger.warning("Scene size is not initialized.")

        # self._selection_stick_service.camera_img = camera_frame.raw_image
        # self._hand_tracking_service.camera_img = camera_frame.raw_image

        phys_obj_model: PhysicalObjectsModel = self.objects_view.model()
        if self.track_objects_checkbox.isChecked():
            scene_phys_objs_names = phys_obj_model.get_scene_physical_objects_names()
            if scene_phys_objs_names is not None and len(scene_phys_objs_names) > 0:

                # TODO: what if I gave the camera service over to the request
                #  (or even didn't give anything an the object detector took the
                #   image itself from the camera service -- this is not good, give the service over
                #   because what if the object detector didn't know how to get the camera frame?)....
                #   Anyways, what if you gave the camera service over instead of the frame, and then the
                #   object detector took the frame from the service?
                #  I think it would be faster.
                #  The object detector takes the frame, independent from the main app loop, and updated the
                #  positions of physical objects. It possibly makes the view faster.

                # self._object_detection_service.get_present_objects(camera_frame,
                #                                                    scene_phys_objs_names,
                #                                                    callback=self.on_obj_detection_complete)

                self._object_detection_service.get_present_objects(scene_phys_objs_names,
                                                                   callback=self.on_obj_detection_complete)
        else:
            phys_obj_model.update_present_physical_objects(None)

        self.camera_view.set_camera_frame(camera_frame)


    def on_obj_detection_complete(self, phys_obj_predictions):
        phys_obj_model: PhysicalObjectsModel = self.objects_view.model()
        phys_obj_model.update_present_physical_objects(phys_obj_predictions)

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




