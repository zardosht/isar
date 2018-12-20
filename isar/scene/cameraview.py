import logging
import pickle

from PyQt5.QtGui import QImage, QPixmap, QDragEnterEvent, QDragMoveEvent, QDropEvent, QCursor
from PyQt5.QtWidgets import QLabel

from isar.scene import annotationtool
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

            qfromat = QImage.Format_Indexed8
            if len(self.opencv_img.shape) == 3:  # sahpe[0] = rows, [1] = cols, [2] = channels
                if self.opencv_img.shape[2] == 4:
                    qfromat = QImage.Format_RGBA8888
                else:
                    qfromat = QImage.Format_RGB888

            out_image = QImage(self.opencv_img,
                               self.opencv_img.shape[1], self.opencv_img.shape[0],
                               self.opencv_img.strides[0], qfromat)
            out_image = out_image.rgbSwapped()
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
                self.po_drag_cursor = None
                event.accept()
            else:
                event.ignore()

            print(event)

        def dragMoveEvent(self, event: QDragMoveEvent):
            if event.mimeData().hasFormat(PhysicalObjectsModel.MIME_TYPE):
                if self.po_drag_cursor is None:
                    self.dropping_physical_object = pickle.loads(event.mimeData().data(PhysicalObjectsModel.MIME_TYPE))
                    po_image = self.dropping_physical_object.image
                    height, width, channel = po_image.shape
                    bytes_per_line = 3 * width
                    qimg = QImage(po_image.data, width, height, bytes_per_line, QImage.Format_RGB888)
                    pixmap = QPixmap.fromImage(qimg)
                    cursor = QCursor(pixmap)
                    self.po_drag_cursor = cursor
                    self.setCursor(cursor)
                else:
                    self.setCursor(self.po_drag_cursor)
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

