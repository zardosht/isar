import cv2

from isar.handskilllearning.handskill_annotation import CurveAnnotation
from isar.scene import sceneutil
from isar.scene.annotationtool import AnnotationTool
from isar.scene.sceneutil import Frame


class CurveAnnotationTool(AnnotationTool):
    global line_coordinates

    def __init__(self):
        super(CurveAnnotationTool, self).__init__()

    def mouse_press_event(self, camera_view, event):
        self.set_drawing(True)
        self.annotation = CurveAnnotation()

        # convert mouse coordinates to image coordinates
        camera_view_size = Frame(camera_view.size().width(), camera_view.size().height())
        img_x, img_y = sceneutil.mouse_coordinates_to_image_coordinates(
            event.pos().x(), event.pos().y(), camera_view_size, self._image_frame)

        line_coordinates.append((img_x, img_y))

    def mouse_move_event(self, camera_view, event):
        if self._drawing:
            camera_view_size = Frame(camera_view.size().width(), camera_view.size().height())
            img_x, img_y = sceneutil.mouse_coordinates_to_image_coordinates(
                event.pos().x(), event.pos().y(), camera_view_size, self._image_frame)

            line_coordinates.append((img_x, img_y))

    def mouse_release_event(self, camera_view, event):
        camera_view_size = Frame(camera_view.size().width(), camera_view.size().height())
        img_x, img_y = sceneutil.mouse_coordinates_to_image_coordinates(
            event.pos().x(), event.pos().y(), camera_view_size, self._image_frame)

        line_coordinates.append((img_x, img_y))

        if self.is_annotation_valid():
            self.annotation.line_coordinates.set_value(line_coordinates)
            self.annotations_model.add_annotation(self.annotation)

        self.set_drawing(False)

    def draw(self):
        if not self._drawing:
            return

        if not self.annotation or not self.annotation.line_coordinates.get_value():
            return

        if self.is_annotation_valid():
            for i in range(len(self.line_coordinates)):
                start = sceneutil.convert_object_to_image(self.line_coordinates[i], self.phys_obj, self.scene_rect,
                                                          self.scene_scale_factor)
                end = sceneutil.convert_object_to_image(self.line_coordinates[i + 1], self.phys_obj,
                                                        self.scene_rect, self.scene_scale_factor)
                cv2.line(self._img, start, end, self.annotation.color.get_value(),
                         self.annotation.thickness.get_value())

    def is_annotation_valid(self):
        # Are there any coordinates saved?
        if len(self.annotation.line_coordinates) is 0:
            return False
        return True
