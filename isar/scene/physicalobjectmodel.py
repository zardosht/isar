import logging
import math
import pickle

from PyQt5.QtCore import QAbstractListModel, Qt, QMimeData, QModelIndex
from PyQt5.QtGui import QBrush

from isar.scene.scenemodel import Scene
from isar.scene.util import RefFrame

"""
Objects can be added in two ways to the scene: 
    a) 
    By drag-n-drop from the object list (in that case the template image of the object is shown on the scene). 
    You can have multiple instances of the same object at the same time on the scene. Those instances are either a template image or the real object.

    b) 
    By putting them on the table. 

The physical objects view shows the list of the object classes that can be added to the scene. If an object class is added to the scene (one or multiples instances of it), then that object class is highlighted in the physical objects view. 

To remove a physical object instance from the scene the user either remove it from the table (if it is on the table) or uses the delete tool to remove it.

The attach to combo box shows a list of instance of the objects available on the scene. 

When a physical object is removed form the scene the annotations attached to it remain in the scene, but are not attached to it. If the user want to also remove those annotations, he uses the delete tool. 

"""

logger = logging.getLogger("isar.physicalobjectmodel")


class PhysicalObjectsModel(QAbstractListModel):

    MIME_TYPE = "application/isar.physical_object"

    def __init__(self):
        super().__init__()
        self.current_annotation = None
        self.__scene: Scene = None
        self.__all_physical_objects = None
        self.__present_physical_objects = {}

    def set_scene(self, scene: Scene):
        self.__scene = scene

    def rowCount(self, parent=None):
        if self.__all_physical_objects is None:
            return 0

        return len(self.__all_physical_objects)

    def data(self, index, role):
        if self.__all_physical_objects is None:
            return

        if not index.isValid():
            return

        physical_object = self.__all_physical_objects[index.row()]
        if role == Qt.DisplayRole:
            return physical_object.name

        if role == Qt.BackgroundColorRole:
            if self.is_contained_in_scene(physical_object):
                return QBrush(Qt.cyan)

    def flags(self, index):
        return super().flags(index) | Qt.ItemIsDragEnabled

    def mimeTypes(self):
        return [PhysicalObjectsModel.MIME_TYPE]

    def mimeData(self, indexs):
        physical_object = self.__all_physical_objects[indexs[0].row()]
        if physical_object in self.get_scene_physical_objects():
            return None

        mime_data = QMimeData()
        bstream = pickle.dumps(physical_object)
        mime_data.setData(PhysicalObjectsModel.MIME_TYPE, bstream)
        return mime_data

    def supportedDropActions(self):
        return Qt.CopyAction

    def is_contained_in_scene(self, physical_obj):
        if self.get_scene_physical_objects() is None or \
                len(self.get_scene_physical_objects()) == 0:
            return False

        return physical_obj in self.get_scene_physical_objects()

    def set_all_physical_objects(self, all_po_s):
        self.__all_physical_objects = all_po_s

    def get_physical_object_at(self, index: QModelIndex):
        if self.__all_physical_objects is None or len(self.__all_physical_objects) == 0:
            return None

        if index is None:
            return None

        if not index.isValid():
            return None

        return self.__all_physical_objects[index.row()]

    def get_scene_physical_objects(self):
        if self.__scene is not None:
            return self.__scene.get_physical_objects()
        else:
            return ()

    def update_present_physical_objects(self, phys_obj_predictions):
        if phys_obj_predictions is None:
            if len(self.__present_physical_objects) == 0:
                return

            self.__present_physical_objects.clear()
            scene_phys_objs = self.get_scene_physical_objects()
            for phys_obj in scene_phys_objs:
                phys_obj.update_tracking(None)
            return

        scene_phys_objs = self.get_scene_physical_objects()
        for obj_detector in phys_obj_predictions:
            present_phys_objs = []
            predictions = phys_obj_predictions[obj_detector]
            if predictions is None or len(predictions) == 0:
                continue

            for scene_phys_obj in scene_phys_objs:
                for prediction in predictions:
                    if scene_phys_obj.name == prediction.label:
                        scene_phys_obj.update_tracking(prediction)
                        present_phys_objs.append(scene_phys_obj)
            self.__present_physical_objects[obj_detector] = present_phys_objs

    def get_present_physical_objects(self):
        result = []
        for obj_detector in self.__present_physical_objects:
            result.extend(self.__present_physical_objects[obj_detector])

        scene_phys_objs = self.get_scene_physical_objects()
        for phys_obj in scene_phys_objs:
            if phys_obj not in result:
                phys_obj.update_tracking(None)

        return tuple(result)

    def add_physical_object_to_scene(self, po):
        self.__scene.add_physical_object(po)


class PhysicalObject:
    def __init__(self):
        self.name = ""
        self.template_image_path = ""
        self.template_image = None
        self.__scene_position = None
        self.__scene_frame = None
        self.__annotations = []

        self._tracking = False
        self.detection_confidence = None
        self.__top_left = None
        self.bottom_right = None
        self.scene_image = None
        self.pose_estimation = None

    @property
    def top_left(self):
        return self.__top_left

    @top_left.setter
    def top_left(self, value):
        self.__top_left = value
        self.__scene_position = value

    @property
    def scene_position(self):
        return self.__scene_position

    @scene_position.setter
    def scene_position(self, scene_position):
        self.__scene_position = scene_position

    @property
    def scene_frame(self):
        return self.__scene_frame

    @scene_frame.setter
    def scene_frame(self, scene_frame):
        self.__scene_frame = scene_frame

    @property
    def ref_frame(self):
        if self.__top_left is None:
            x, y = self.__scene_position
            width = self.template_image.shape[1]
            height = self.template_image.shape[0]
        else:
            x, y = self.__top_left
            br_x, br_y = self.bottom_right
            width = math.fabs(br_x - x)
            height = math.fabs(br_y - y)

        return RefFrame(x, y, width, height)

    def get_annotations(self):
        return tuple(self.__annotations)

    def remove_annotation(self, annotation):
        self.__annotations.remove(annotation)

    def add_annotation(self, annotation):
        if annotation not in self.__annotations:
            annotation.owner = self
            self.__annotations.append(annotation)

    def update_tracking(self, prediction):
        if prediction is None:
            self._tracking = False
            self.detection_confidence = None
            self.__top_left = None
            self.bottom_right = None
            self.pose_estimation = None
            self.scene_image = None
        else:
            self._tracking = True
            self.detection_confidence = prediction.confidence
            self.top_left = prediction.top_left
            self.bottom_right = prediction.bottom_right
            self.pose_estimation = prediction.pose_estimation
            self.scene_image = prediction.image

    def is_tracking(self):
        return self._tracking

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return isinstance(other, PhysicalObject) and self.name == other.name

