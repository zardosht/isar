import logging
import pickle

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QPixmap, QDragEnterEvent, QDragMoveEvent, QDropEvent, QCursor
from PyQt5.QtWidgets import QLabel

from isar.scene import annotationtool, util, physicalobjecttool
from isar.scene.physicalobjectmodel import PhysicalObjectsModel
from isar.scene.util import Frame

logger = logging.getLogger("isar.cameraview")


class CameraView(QLabel):
        def __init__(self, parent=None, scene_definition_window=None):
            super(CameraView, self).__init__(parent)
            self.scene_definition_windows = scene_definition_window

            self.opencv_img = None
            self.image_frame = None
            self.active_annotation_tool = None
            self.annotations_model = None
            self.physical_objects_model: PhysicalObjectsModel = None

            self.setAcceptDrops(True)
            self.dropped_physical_object = None

            self.setMouseTracking(True)
            self.camera_view_size = Frame(self.size().width(), self.size().height())

        def set_camera_frame(self, camera_frame):
            self.opencv_img = camera_frame.scene_image
            self.image_frame = Frame(self.opencv_img.shape[1], self.opencv_img.shape[0])

            self.draw_scene_physical_objects()

            self.draw_scene_annotations()

            if self.active_annotation_tool:
                self.active_annotation_tool.set_image(self.opencv_img)
                self.active_annotation_tool.annotations_model = self.annotations_model
                self.active_annotation_tool.draw()

            out_image = util.get_qimage_from_np_image(self.opencv_img)
            # out_image = out_image.mirrored(horizontal=True, vertical=False)
            self.setPixmap(QPixmap.fromImage(out_image))
            self.setScaledContents(True)
            self.update()

        def draw_scene_annotations(self):
            if self.annotations_model is None or \
                    self.annotations_model.get_scene_annotations() is None or \
                    len(self.annotations_model.get_scene_annotations()) == 0:
                return

            for annotation in self.annotations_model.get_scene_annotations():
                annotationtool.draw_annotation(self.opencv_img, annotation)

        def draw_scene_physical_objects(self):
            if self.physical_objects_model is None or \
                    self.physical_objects_model.get_scene_physical_objects() is None or \
                    len(self.physical_objects_model.get_scene_physical_objects()) == 0:
                return

            scene_phys_objs = self.physical_objects_model.get_scene_physical_objects()
            present_phys_objs = self.physical_objects_model.get_present_physical_objects()
            if present_phys_objs is None:
                logger.warning("Present physical objects is None!")
                return

            for phys_obj in scene_phys_objs:
                if phys_obj in present_phys_objs:
                    physicalobjecttool.draw_physical_object_bounding_box(self.opencv_img, phys_obj)
                else:
                    physicalobjecttool.draw_physical_object_image(self.opencv_img, phys_obj)

                self.draw_physical_object_annotations(phys_obj)

        def draw_physical_object_annotations(self, phys_obj):
            if phys_obj is None or phys_obj.get_annotations() is None or len(phys_obj.get_annotations()) == 0:
                return

            for annotation in phys_obj.get_annotations():
                annotationtool.draw_annotation(self.opencv_img, annotation, phys_obj.ref_frame)

        def dragEnterEvent(self, event: QDragEnterEvent):
            if event.mimeData().hasFormat(PhysicalObjectsModel.MIME_TYPE):
                self.active_annotation_tool = None
                event.accept()
            else:
                event.ignore()

            print(event)

        def dragMoveEvent(self, event: QDragMoveEvent):
            if event.mimeData().hasFormat(PhysicalObjectsModel.MIME_TYPE):
                event.accept()
            else:
                event.ignore()

        def dropEvent(self, event: QDropEvent):
            if event.mimeData().hasFormat(PhysicalObjectsModel.MIME_TYPE):
                dropped_po = pickle.loads(event.mimeData().data(PhysicalObjectsModel.MIME_TYPE))
                if dropped_po:
                    self.dropped_physical_object = dropped_po

                    self.physical_objects_model.add_physical_object_to_scene(dropped_po)
                    dropped_po.scene_position = util.mouse_coordinates_to_image_coordinates(
                        event.pos().x(), event.pos().y(), self.camera_view_size, self.image_frame)
                    event.setDropAction(Qt.CopyAction)
                    event.accept()
                else:
                    event.ignore()
            else:
                event.ignore()

        def mousePressEvent(self, event):
            if self.active_annotation_tool:
                self.active_annotation_tool.mouse_press_event(self, event)

            super().mousePressEvent(event)

        def mouseMoveEvent(self, event):
            if self.image_frame is not None:
                img_x, img_y = util.mouse_coordinates_to_image_coordinates(
                    event.pos().x(), event.pos().y(), self.camera_view_size, self.image_frame)
                self.scene_definition_windows.update_mouse_position_label((img_x, img_y))

                mouse_on_object = False
                for phys_obj in self.physical_objects_model.get_scene_physical_objects():
                    if util.intersects_with_phys_obj((img_x, img_y), phys_obj):
                        phys_obj_name = phys_obj.name
                        obj_x, obj_y = util.convert_image_to_object((img_x, img_y), phys_obj.ref_frame)
                        self.scene_definition_windows.update_mouse_position_label((obj_x, obj_y), phys_obj_name)
                        mouse_on_object = True
                        break

                if not mouse_on_object:
                    self.scene_definition_windows.update_mouse_position_label(None, None)

            if self.active_annotation_tool:
                self.active_annotation_tool.mouse_move_event(self, event)

            super().mouseMoveEvent(event)

        def mouseReleaseEvent(self, event):
            if self.active_annotation_tool:
                self.active_annotation_tool.mouse_release_event(self, event)

            super().mouseReleaseEvent(event)

        def set_active_annotation_tool(self, annotation_btn_name, ):
            if not annotation_btn_name:
                self.active_annotation_tool = None
            else:
                self.active_annotation_tool = annotationtool.annotation_tool_btns[annotation_btn_name]
                self.active_annotation_tool.annotations_model = self.annotations_model

        def resizeEvent(self, resize_event):
            self.camera_view_size = Frame(self.size().width(), self.size().height())
