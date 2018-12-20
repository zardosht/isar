import logging
import pickle

from PyQt5.QtGui import QImage, QPixmap, QDragEnterEvent, QDragMoveEvent, QDropEvent, QCursor
from PyQt5.QtWidgets import QLabel

from isar.scene import annotationtool, util
from isar.scene.physicalobjectmodel import PhysicalObjectsModel

logger = logging.getLogger("isar.cameraview")


class CameraView(QLabel):
        def __init__(self, parent=None):
            super(CameraView, self).__init__(parent)
            self.opencv_img = None
            self.active_annotation_tool = None
            self.annotations_model = None

            self.setAcceptDrops(True)
            self.po_drag_cursor = None

        def set_camera_frame(self, camera_frame):
            self.opencv_img = camera_frame.image

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
            print(event)

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

