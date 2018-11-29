from PyQt5 import QtGui, QtCore
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QWidget, QLabel

from isar.scene.annotationtool import LineAnnotationTool


class CameraView(QLabel):

        def __init__(self, parent=None):
            super(CameraView, self).__init__(parent)
            self.opencv_img = None
            self.active_annotation_tool = LineAnnotationTool()

        def set_camera_frame(self, camera_frame):
            self.opencv_img = camera_frame.image

            self.active_annotation_tool.img = self.opencv_img
            self.active_annotation_tool.draw()
            # do some stuff if needed

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

        def mousePressEvent(self, event):
            # TODO: froward event to the active annotation tool
            self.active_annotation_tool.mouse_press_event(event)
            super().mousePressEvent(event)

        def mouseMoveEvent(self, event):
            # TODO: froward event to the active annotation tool
            self.active_annotation_tool.mouse_move_event(event)
            super().mouseMoveEvent(event)

        def mouseReleaseEvent(self, event):
            # TODO: froward event to the active annotation tool
            self.active_annotation_tool.mouse_release_event(event)
            super().mouseReleaseEvent(event)