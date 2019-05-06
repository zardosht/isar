import logging

from isar.scene import annotationtool, physicalobjecttool


logger = logging.getLogger("isar.scene.scenerenderer")


class SceneRenderer:
    def __init__(self):
        self.__annotations_model = None
        self.__physical_objects_model = None
        self.opencv_img = None
        self.scene_rect = None
        self.scene_scale_factor = None

    def set_annotations_model(self, annotations_model):
        self.__annotations_model = annotations_model

    def set_physical_objects_model(self, phm):
        self.__physical_objects_model = phm

    def draw_scene_annotations(self):
        if self.__annotations_model is None or \
                self.__annotations_model.get_scene_annotations() is None or \
                len(self.__annotations_model.get_scene_annotations()) == 0:
            return

        for annotation in self.__annotations_model.get_scene_annotations():
            annotationtool.draw_annotation(self.opencv_img, annotation)

    def draw_scene_physical_objects(self):
        if self.__physical_objects_model is None or \
                self.__physical_objects_model.get_scene_physical_objects() is None or \
                len(self.__physical_objects_model.get_scene_physical_objects()) == 0:
            return

        scene_phys_objs = self.__physical_objects_model.get_scene_physical_objects()
        present_phys_objs = self.__physical_objects_model.get_present_physical_objects()
        if present_phys_objs is None:
            logger.warning("Present physical objects is None!")
            return

        for phys_obj in scene_phys_objs:
            if phys_obj in present_phys_objs:
                physicalobjecttool.draw_physical_object_bounding_box(self.opencv_img, phys_obj, self.scene_rect)
                self.draw_physical_object_annotations(phys_obj, self.scene_rect, None)
            else:
                physicalobjecttool.draw_physical_object_image(self.opencv_img, self.scene_scale_factor, phys_obj)
                self.draw_physical_object_annotations(phys_obj, None, self.scene_scale_factor)

    def draw_physical_object_annotations(self, phys_obj, scene_rect, scene_scale_factor):
        if phys_obj is None or phys_obj.get_annotations() is None or len(phys_obj.get_annotations()) == 0:
            return

        for annotation in phys_obj.get_annotations():
            annotationtool.draw_annotation(self.opencv_img, annotation, phys_obj, scene_rect, scene_scale_factor)




