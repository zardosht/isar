import logging
import pickle

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QPixmap, QDragEnterEvent, QDragMoveEvent, QDropEvent, QCursor
from PyQt5.QtWidgets import QLabel, QMessageBox

from isar.scene import annotationtool, sceneutil, physicalobjecttool
from isar.scene.physicalobjectmodel import PhysicalObjectsModel
from isar.scene.scenerenderer import SceneRenderer
from isar.scene.sceneutil import Frame

logger = logging.getLogger("isar.scene.cameraview")


class CameraView(QLabel):
        def __init__(self, parent=None, scene_definition_window=None):
            super(CameraView, self).__init__(parent)
            self.scene_definition_windows = scene_definition_window
            self.scene_renderer = SceneRenderer()

            self.opencv_img = None
            self.image_frame = None
            self.active_annotation_tool = None
            self.__annotations_model = None
            self.__physical_objects_model: PhysicalObjectsModel = None

            self.scene_renderer.set_annotations_model(self.__annotations_model)
            self.scene_renderer.set_physical_objects_model(self.__physical_objects_model)

            self.setAcceptDrops(True)
            self.dropped_physical_object = None

            self.setMouseTracking(True)
            self.camera_view_size = Frame(self.size().width(), self.size().height())

        def set_annotations_model(self, annotations_model):
            self.__annotations_model = annotations_model
            self.scene_renderer.set_annotations_model(self.__annotations_model)

        def set_physical_objects_model(self, phm):
            self.__physical_objects_model = phm
            self.scene_renderer.set_physical_objects_model(self.__physical_objects_model)

        def set_camera_frame(self, camera_frame):
            if not self.scene_definition_windows.scene_size_initialized:
                logger.warning("Scene size is not initialized.")
                self.opencv_img = camera_frame.scene_image
            else:
                self.scene_renderer.scene_rect = self.scene_definition_windows.scene_rect
                x, y, width, height = self.scene_definition_windows.scene_rect
                self.opencv_img = camera_frame.scene_image[y:y + height, x:x + width].copy()

            self.scene_renderer.opencv_img = self.opencv_img
            self.image_frame = Frame(self.opencv_img.shape[1], self.opencv_img.shape[0])

            self.scene_renderer.draw_scene_physical_objects()

            self.scene_renderer.draw_scene_annotations()

            if self.active_annotation_tool:
                self.active_annotation_tool.set_image(self.opencv_img)
                self.active_annotation_tool.annotations_model = self.__annotations_model
                self.active_annotation_tool.draw()

            out_image = sceneutil.get_qimage_from_np_image(self.opencv_img)
            # out_image = out_image.mirrored(horizontal=True, vertical=False)
            self.setPixmap(QPixmap.fromImage(out_image))
            self.setScaledContents(True)
            self.update()

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
            if not self.scene_definition_windows.scene_size_initialized:
                QMessageBox.warning(None, "Error", "Scene size is not initialized!")
                event.ignore()
                return

            if event.mimeData().hasFormat(PhysicalObjectsModel.MIME_TYPE):
                dropped_po = pickle.loads(event.mimeData().data(PhysicalObjectsModel.MIME_TYPE))
                if dropped_po:
                    self.dropped_physical_object = dropped_po

                    self.__physical_objects_model.add_physical_object_to_scene(dropped_po)
                    dropped_po.scene_position = sceneutil.mouse_coordinates_to_image_coordinates(
                        event.pos().x(), event.pos().y(), self.camera_view_size, self.image_frame)
                    event.setDropAction(Qt.CopyAction)
                    event.accept()
                else:
                    event.ignore()
            else:
                event.ignore()

        def mousePressEvent(self, event):
            if self.active_annotation_tool:
                if not self.scene_definition_windows.scene_size_initialized:
                    QMessageBox.warning(None, "Error", "Scene size is not initialized!")
                else:
                    self.active_annotation_tool.mouse_press_event(self, event)

            super().mousePressEvent(event)

        def mouseMoveEvent(self, event):
            if self.scene_definition_windows is None:
                super().mouseMoveEvent(event)
                return

            if self.image_frame is not None:
                img_x, img_y = sceneutil.mouse_coordinates_to_image_coordinates(
                    event.pos().x(), event.pos().y(), self.camera_view_size, self.image_frame)
                self.scene_definition_windows.update_mouse_position_label((img_x, img_y))

                mouse_on_object = False
                for phys_obj in self.__physical_objects_model.get_scene_physical_objects():
                    if sceneutil.intersects_with_phys_obj((img_x, img_y), phys_obj):
                        phys_obj_name = phys_obj.name
                        obj_x, obj_y = sceneutil.convert_image_to_object((img_x, img_y), phys_obj.ref_frame)
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
                self.active_annotation_tool.annotations_model = self.__annotations_model

        def resizeEvent(self, resize_event):
            self.camera_view_size = Frame(self.size().width(), self.size().height())



