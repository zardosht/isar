import logging

from isar.scene.physicalobjectmodel import PhysicalObjectsModel
from isar.services.service import Service

logger = logging.getLogger("isar.objecttrackingservice")


"""
Keeps track of which objects are on the table, and fires PhysicalObjectAppeared, PhysicalObjectDisappeared, 
PhysicalObjectPicked, and PhysicalObjectGroupAppeared events. 
"""


class ObjectTrackingService(Service):
    def __init__(self, service_name):
        super().__init__(service_name)

        self.__annotations_model = None
        self.__scenes_model = None
        self.__physical_objects_model = None

        self.current_scene = None

    def set_annotations_model(self, annotations_model):
        self.__annotations_model = annotations_model

    def set_scenes_model(self, scenes_model):
        self.__scenes_model = scenes_model

    def set_physical_objects_model(self, phys_objs_model):
        self.__physical_objects_model = phys_objs_model
        self.__physical_objects_model.tracking_lost.connect(self.tracking_lost)
        self.__physical_objects_model.tracking_captured.connect(self.tracking_captured)

    def set_current_scene(self, current_scene):
        self.current_scene = current_scene

    def tracking_lost(self, phys_obj):
        logger.info("Tracking lost: {}".format(phys_obj.name))

    def tracking_captured(self, phys_obj):
        logger.info("Tracking captured: {}".format(phys_obj.name))

    def stop(self):
        pass
