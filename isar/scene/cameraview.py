from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QLabel

from isar.scene import annotationtool
from isar.scene.annotationtool import LineAnnotationTool, RectangleAnnotationTool, CircleAnnotationTool, \
    SelectAnnotationTool


class CameraView(QLabel):

        def __init__(self, parent=None):
            super(CameraView, self).__init__(parent)
            self.opencv_img = None
            self.active_annotation_tool = None
            self.scene = None

        def set_camera_frame(self, camera_frame):
            self.opencv_img = camera_frame.image

            self.draw_scene_annotations()

            if self.active_annotation_tool:
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
            if not self.scene or not self.scene.annotations:
                return

            for annotation in self.scene.annotations:
                annotationtool.draw_annotation(self.opencv_img, annotation)

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

        def set_active_annotation_tool(self, annotation_btn_name):
            if not annotation_btn_name:
                self.active_annotation_tool = None
            else:
                self.active_annotation_tool = annotation_tool_btns[annotation_btn_name]()


annotation_tool_btns = {
    "line_btn": LineAnnotationTool,
    "rectangle_btn": RectangleAnnotationTool,
    "circle_btn": CircleAnnotationTool,
    "select_btn": SelectAnnotationTool
}