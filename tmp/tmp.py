
class MyClass:
    def a_method(self):
        print("MyClass.a_method()")


def a_method():
    pass


# # ============================================================================
#
# phys_obj_predictions = {}
#
# phys_obj_predictions["aa"] = [1, 2, 3]
# phys_obj_predictions["bb"] = [4, 5, 6]
#
# for key in phys_obj_predictions:
#     print(key)
#     print(phys_obj_predictions[key])
#
#
# # ============================================================================
# from PyQt5.QtGui import QFont, QColor
# from PyQt5.QtCore import QAbstractItemModel, QModelIndex, Qt, QAbstractListModel, QAbstractTableModel, QSize, QVariant
# from PyQt5.QtWidgets import QApplication, QTreeView, QTableView, QListView
#
#
# class NodeTree(QAbstractItemModel):
#     def __init__(self, parent, data):
#         super(NodeTree, self).__init__(parent)
#         self.data = data
#
#     def rowCount(self, parent=QModelIndex()):
#         # int rowCount (self, QModelIndex parent = QModelIndex())
#         if parent.isValid():
#             data = self.data
#             for idx in parent.internalPointer():
#                 data = data[idx]
#             return len(data)
#         else:
#             return len(self.data)
#
#     def columnCount(self, parent=QModelIndex()):
#         # int columnCount (self, QModelIndex parent = QModelIndex())
#         return 1
#
#     def data(self, index=QModelIndex(), role=None):
#         # QVariant data (self, QModelIndex index, int role = Qt.DisplayRole)
#         if role == 0:
#             if index.isValid():
#                 return str(index.internalPointer())
#             else:
#                 return "No Data"
#         return None
#
#     def index(self, row, col, parent=QModelIndex()):
#         # QModelIndex index (self, int row, int column, QModelIndex parent = QModelIndex())
#         # QModelIndex createIndex (self, int arow, int acolumn, int aid)
#         # QModelIndex createIndex (self, int arow, int acolumn, object adata = 0)
#         if parent.isValid():
#             ptr = [parent.internalPointer(), row]
#             #     return self.createIndex(row,col,ptr)
#             return QModelIndex()
#         else:
#             ptr = [row]
#             #    return self.createIndex(row,col,ptr)
#             return QModelIndex()
#         return QModelIndex()
#
#     def parent(self, child=QModelIndex()):
#         # QObject parent (self)
#         if child.isValid():
#             print(child.internalPointer())
#         return QModelIndex()
#
#
# if __name__ == "__main__":
#     # http://blog.mathieu-leplatre.info/filesystem-watch-with-pyqt4.html
#     import sys
#
#     app = QApplication(sys.argv)
#     TreeView = QTreeView()
#     TreeModel = NodeTree(TreeView, [['A', ['a', 1]], ['C', 'D'], ['E', 'F']])
#     TreeView.setModel(TreeModel)
#     TreeView.show()
#     app.exec_()
#
# # ============================================================================
# a = float(12.3)
# b = float(12)
#
# print(a)
# print(b)
#
#
#
# # ============================================================================
# from ast import literal_eval
#
# a = literal_eval("\"jfkddkke ekeeke eekekke kek ek e\"")
# print(a)
#
# # ============================================================================
# from array import array
#
# a = (1, 2)
# b = (1, 2) * 3
# c = [1, 2] * 3
# d = 3 * array('i', a)
#
# print(b)
# print(c)
# print(d)
#
# #  ============================================================================
#
#
# class Parent:
#     def __init__(self):
#         self.foo = 3
#
#     def do_something(self):
#         print("Parent.do_something(). self.foo is: ", self.foo)
#         self.do_another_thing()
#
#     def do_another_thing(self):
#         print("Parent.do_another_thing()")
#
#
# class Child(Parent):
#     def __init__(self):
#         self.foo = 5
#
#     def do_something(self):
#         print("Child.do_something()")
#         super().do_something()
#
#     def do_another_thing(self):
#         print("Child.do_another_thing()")
#
#
# child = Child()
# child.do_something()
#
#
# #  ============================================================================
#
#
# class Vehicle:
#     kind = 'car'
#
#     def __init__(self, manufacturer, model):
#         self.manufacturer = manufacturer
#         self.model_name = model
#
#     @property
#     def name(self):
#         return "%s %s" % (self.manufacturer, self.model_name)
#
#     def __repr__(self):
#         return "<%s>" % self.name
#
#
# car = Vehicle('Toyota', 'Corolla')
# print(car, car.kind)
#
# #  ============================================================================
#
#
# class A(object):
#     def __init__(self):
#         self.name = "A"
#         super(A, self).__init__()
#
#     def Update(self):
#         print("Update A")
#         self.PickTarget()
#
#     def PickTarget(self):
#         print("PickTarget A")
#
#
# class B(object):
#     def __init__(self):
#         self.name = "B"
#         super(B, self).__init__()
#
#     def Update(self):
#         print("Update B")
#         B.PickTarget(self)
#
#     def PickTarget(self):
#         print("PickTarget B")
#
#
# class C(A, B):
#     def __init__(self):
#         super(C, self).__init__()
#
#     def Update(self, useA):
#         if useA:
#             A.Update(self)
#         else:
#             B.Update(self)
#
#
# c = C()
# c.Update(useA = True)
# # prints:
# # Update A
# # PickTarget A
#
# c.Update(useA = False)
# # prints:
# # Update B
# # PickTarget A
#
#
# # ============================================================================
#
#
# class A:
#     def foo(self):
#         print("A.foo")
#
#
# class B(A):
#     pass
#
#
# class C(A):
#     def foo(self):
#         print("C.foo")
#
#
# class D(B, C):
#     pass
#
#
# d = D()
# print(D.mro())
# d.foo()
#
#
# # ============================================================================
#
#
# class SimpleList:
#     def __init__(self, items):
#         print("Init in SimpleList")
#         self._items = list(items)
#
#     def add(self, item):
#         print("SimpleList.add()")
#         self._items.append(item)
#
#     def __getitem__(self, index):
#         return self._items[index]
#
#     def sort(self):
#         self._items.sort()
#
#     def __len__(self):
#         return len(self._items)
#
#     def __repr__(self):
#         return "{}({!r})".format(
#             self.__class__.__name__,
#             self._items)
#
#
# class SortedList(SimpleList):
#     def __init__(self, items = ()):
#         print("Init in SortedList")
#         super().__init__(items)
#         self.sort()
#
#     def add(self, item):
#         print("SortedList.add()")
#         super().add(item)
#         self.sort()
#
#
# class IntList(SimpleList):
#     def __init__(self, items=()):
#         print("Init in IntList")
#         for item in items:
#             self._validate(item)
#         super().__init__(items)
#
#     @classmethod
#     def _validate(cls, item):
#         if not isinstance(item, int):
#             raise TypeError(
#                 '{} only supports integer values.'.format(
#                     cls.__name__))
#
#     def add(self, item):
#         print("IntList.add()")
#         self._validate(item)
#         super().add(item)
#
#
# class SortedIntList(IntList, SortedList):
#     pass
#
#
# sil = SortedIntList([23, 42, 2])
# print(sil)
# sil.add(-12)
# print(sil)
# print(SortedIntList.mro())
#
#
# # ============================================================================
#
#
# class Base1:
#     def __init__(self):
#         print("Init in Base1")
#         super().__init__()
#
#     def foo(self, name):
#         print("Foo in Base1 {0}, {1}".format(name, self.__class__))
#         super(Base1, self).foo(name)
#
#
# class Base2:
#     def __init__(self):
#         print("Init in Base2")
#
#     def foo(self, name):
#         print("Foo in Base2 {0}, {1}".format(name, self.__class__))
#
#
# class Child(Base1, Base2):
#     def __init__(self):
#         super().__init__()
#         print("Init in Child")
#
#     def foo(self, name):
#         print("Foo in Child {0}, {1}".format(name, self.__class__))
#         Base2.foo(self, None)
#
#
# def main():
#     child = Child()
#     child.foo("Zari")
#     print(type(child).mro())
#
#
# if __name__ == "__main__":
#     main()
#
#
# # ============================================================================
#
# class Foo:
#     def __init__(self):
#         self._bar = None
# 
# 
# class Buz:
#     def __init__(self):
#         self.buz = "Buz"
# 
# 
# foo = Foo()
# buz = Buz()
# 
# # print(foo.bar)
# foo.bar = buz
# foo.bing = 1
# foo.crazy_lang = "Python"
# print(foo.bar)
