from PyQt5 import QtGui, QtCore
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QWidget, QLabel

from isar.scene.annotationtool import LineAnnotationTool
from isar.scene.scenemodel import Scene
from isar.scene import annotationtool


class CameraView(QLabel):

        def __init__(self, parent=None):
            super(CameraView, self).__init__(parent)
            self.opencv_img = None

            # TODO: this must be set from definition window whenever a tool button is clicked and is active.
            # TODO: the buttons in definition window must be toggle buttons
            self.active_annotation_tool = LineAnnotationTool()

            self.scene = None

        def set_camera_frame(self, camera_frame):
            self.opencv_img = camera_frame.image

            self.draw_scene_annotations()

            self.active_annotation_tool.img = self.opencv_img
            self.active_annotation_tool.scene = self.scene
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
            for annotation in self.scene.annotations:
                annotationtool.draw_annotation(self.opencv_img, annotation)

        def mousePressEvent(self, event):
            self.active_annotation_tool.mouse_press_event(self, event)
            super().mousePressEvent(event)

        def mouseMoveEvent(self, event):
            self.active_annotation_tool.mouse_move_event(self, event)
            super().mouseMoveEvent(event)

        def mouseReleaseEvent(self, event):
            self.active_annotation_tool.mouse_release_event(self, event)
            super().mouseReleaseEvent(event)