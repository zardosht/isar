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

            self.draw_scene_annotations()
            self.draw_unpresent_scene_physical_objects()
            self.draw_present_scene_physical_objects()

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

        def draw_unpresent_scene_physical_objects(self):
            if not self.physical_objects_model or not self.physical_objects_model.get_scene_physical_objects():
                return

            scene_phys_objs = self.physical_objects_model.get_scene_physical_objects()
            present_instances = self.physical_objects_model.get_num_present_instances()
            draw = False
            for phys_obj in scene_phys_objs:
                name = phys_obj.name
                if name in present_instances:
                    if present_instances[name] == 0:
                        draw = True
                    else:
                        present_instances[name] -= 1
                        draw = False
                        continue
                else:
                    draw = True
                if draw:
                    physicalobjecttool.draw_physical_object(self.opencv_img, phys_obj)
                    draw = False

        def draw_present_scene_physical_objects(self):
            # TODO: draw bounding boxes
            pass

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
                    dropped_po.scene_position = \
                        (event.pos().x() / self.size().width(), event.pos().y() / self.size().height())

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

