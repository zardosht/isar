from PyQt5 import QtCore
from PyQt5.QtCore import QAbstractListModel, Qt

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


class PhysicalObjectsModel(QAbstractListModel):
    editCompleted = QtCore.pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.current_annotation = None
        self.__scene = None
        self.__physical_objects = None

    def rowCount(self, parent=None):
        if self.__physical_objects is None:
            return 0

        return len(self.__physical_objects)

    def data(self, index, role):
        if self.__physical_objects is None:
            return

        if role == QtCore.Qt.DisplayRole:
            return self.__physical_objects[index.row()].name

    def flags(self, index):
        return Qt.ItemIsSelectable | Qt.ItemIsEnabled


class PhysicalObject:
    def __init__(self):
        self.name = ""
        self.image_path = ""
        self.image = None
        self.annotations = []
