import logging
import pickle

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QPixmap, QDragEnterEvent, QDragMoveEvent, QDropEvent, QCursor
from PyQt5.QtWidgets import QLabel

from isar.scene import annotationtool, util, physicalobjecttool
from isar.scene.physicalobjectmodel import PhysicalObjectsModel

logger = logging.getLogger("isar.cameraview")


class CameraView(QLabel):
        def __init__(self, parent=None):
            super(CameraView, self).__init__(parent)
            self.opencv_img = None
            self.active_annotation_tool = None
            self.annotations_model = None
            self.physical_objects_model: PhysicalObjectsModel = None

            self.setAcceptDrops(True)
            self.dropped_physical_object = None

        def set_camera_frame(self, camera_frame):
            self.opencv_img = camera_frame.image

            self.draw_scene_physical_objects()

            self.draw_scene_annotations()

            if self.active_annotation_tool:
                self.active_annotation_tool.img = self.opencv_img
                self.active_annotation_tool.annotations_model = self.annotations_model
                self.active_annotation_tool.draw()

            out_image = util.get_qimage_from_np_image(self.opencv_img)
            # out_image = out_image.mirrored(horizontal=True, vertical=False)
            self.setPixmap(QPixmap.fromImage(out_image))
            self.setScaledContents(True)
            self.update()

        def draw_scene_annotations(self):
            if not self.annotations_model or not self.annotations_model.get_annotations():
                return

            for annotation in self.annotations_model.get_annotations():
                annotationtool.draw_annotation(self.opencv_img, annotation)

        def draw_scene_physical_objects(self):
            if not self.physical_objects_model or not self.physical_objects_model.get_scene_physical_objects():
                return

            scene_phys_objs = self.physical_objects_model.get_scene_physical_objects()
            present_phys_objs = self.physical_objects_model.get_present_physical_objects()
            for phys_obj in scene_phys_objs:
                if phys_obj in present_phys_objs:
                    physicalobjecttool.draw_physical_object_bounding_box(self.opencv_img, phys_obj)
                else:
                    physicalobjecttool.draw_physical_object_image(self.opencv_img, phys_obj)

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
                    camera_view_size = (self.size().width(), self.size().height())
                    dropped_po.scene_position = util.image_coordinates_to_relative_coordinates(
                        camera_view_size, event.pos().x(), event.pos().y())
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

