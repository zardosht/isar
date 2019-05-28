import random
import sys

from PyQt5 import Qt, QtCore
from PyQt5.QtCore import QAbstractListModel, QModelIndex
from PyQt5.QtWidgets import QApplication, QListView


class RandomList:
    def __init__(self, name):
        self.name = name
        self.data = [i for i in range(random.randint(0, 9))]

    def print_data(self):
        print(self.data)

    def __str__(self):
        return self.name + ": " + str(self.data)


class ActionsModel(QAbstractListModel):
    def __init__(self):
        super().__init__()
        self.actions = []

    def data(self, index, role):
        if role == QtCore.Qt.DisplayRole:
            action = index.internalPointer()
            return action.name
        elif role == QtCore.Qt.UserRole:
            return index.internalPointer()

    def rowCount(self, parent=None):
        return len(self.actions)

    def flags(self, index):
        return QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled

    def index(self, row, column, parent):
        if not self.hasIndex(row, 0, parent):
            return QModelIndex()

        action = self.actions[row]
        return self.createIndex(row, 0, action)

    def add_action(self, action):
        self.actions.append(action)


def list_view_current_changed():
    index = list_view.selectionModel().currentIndex()
    action = list_view.model().data(index, QtCore.Qt.UserRole)
    action.print_data()

    action = index.internalPointer()
    print(str(action))


if __name__ == "__main__":
    app = QApplication(sys.argv)

    list_view = QListView()

    actions_model = ActionsModel()
    actions_model.add_action(RandomList("l1"))
    actions_model.add_action(RandomList("l2"))
    actions_model.add_action(RandomList("l3"))

    list_view.setModel(actions_model)

    list_view.selectionModel().currentChanged.connect(list_view_current_changed)

    list_view.show()
    app.exec_()
