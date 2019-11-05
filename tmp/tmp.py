
import cv2

print(cv2.__version__)






# # ===================================================================
#
# import time
# from multiprocessing import Process, Queue
#
#
# class MyProcess(Process):
#     def __init__(self, rect_queue):
#         super().__init__()
#         self.rect = (-1, -1)
#         self.rect_queue = rect_queue
#
#     def run(self):
#         while True:
#             time.sleep(0.5)
#             aa = int(time.time())
#             try:
#                 self.rect_queue.get_nowait()
#             except:
#                 pass
#
#             self.rect_queue.put((aa, aa + 1))
#
#     def get_rect(self):
#         return self.rect_queue.get()
#
#
# def main():
#     rect_queue = Queue(1)
#     my_process = MyProcess(rect_queue)
#     my_process.start()
#
#     while True:
#         time.sleep(5)
#         rect = my_process.get_rect()
#         print(time.time(), rect)
#
#
# if __name__ == "__main__":
#     main()
#
#
# # ===================================================================
#
# import random
# import time
# from queue import Queue
# from threading import Event, Thread
#
#
# POISON_PILL = "poison_pill"
#
#
# class Item:
#     def __init__(self, item_number):
#         self.item_number = item_number
#
#     def __str__(self):
#         return "Item" + str(self.item_number)
#
#
# class Producer:
#     def __init__(self):
#         self.queue_size = 20
#         self._queue = Queue(self.queue_size)
#         self.stop_event = Event()
#
#     def start(self):
#         t = Thread(target=self._start)
#         t.start()
#         print("producer started")
#
#     def _start(self):
#         item_number = 0
#         while not self.stop_event.is_set():
#             item = Item(item_number)
#             self._queue.put(item)
#             item_number += 1
#
#     def get_item(self):
#         item = self._queue.get()
#         return item
#
#     def stop(self):
#         self.stop_event.set()
#         while not self._queue.empty():
#             self._queue.get()
#
#         while not self._queue.full():
#             print("producer put poison pill")
#             self._queue.put(POISON_PILL)
#
#
# class Consumer:
#     def __init__(self, id):
#         self.id = id
#
#     def start(self):
#         t = Thread(target=self._start)
#         t.start()
#         print("{} started".format(self))
#
#     def _start(self):
#         producer = get_service("producer")
#         while True:
#             time.sleep(random.random())
#
#             item = producer.get_item()
#             if item == POISON_PILL:
#                 print("{} got poison pill. Break.".format(self))
#                 break
#
#             print("{} got item {}".format(self, item))
#
#     def stop(self):
#         pass
#
#     def __str__(self):
#         return "Consumer" + str(self.id)
#
#
# services = {}
# consumers = []
#
#
# def get_service(service_name):
#     return services[service_name]
#
#
# p = Producer()
# services["producer"] = p
# p.start()
#
# c1 = Consumer(1)
# c1.start()
# consumers.append(c1)
#
# c2 = Consumer(2)
# c2.start()
# consumers.append(c2)
#
#
# # c3 = Consumer(1)
# # c3.start()
# # print("Consumer3 started.")
# # consumers.append(c3)
#
#
# print("Waiting on main thread for 10 sec...............")
# time.sleep(10)
# print("Finished waiting on main .......................")
#
# print("Stopping...")
#
# c1.stop()
# print("Consumer1 stopped.")
#
# c2.stop()
# print("Consumer2 stopped.")
#
# c3.stop()
# print("Consumer3 stopped.")
#
# p.stop()
# print("bye")
#
# # ============================================================
#
# import random
# import time
#
# from queue import Empty, Queue
# from threading import Thread
#
# max_product = 10
# cur_product = 0
#
# done = False
#
#
# def produce(queue):
#     global cur_product, done
#     nums = range(5)
#     while True:
#         if cur_product >= max_product:
#             done = True
#             break
#
#         num = random.choice(nums)
#         queue.put(num)
#         print('Produced:', num)
#         time.sleep(random.randint(0, 5))
#
#         cur_product += 1
#
#     print('Exiting producer thread...')
#
#
# def consume(name, queue):
#     while not done:
#         try:
#             num = queue.get(timeout=0.1)
#             queue.task_done()
#             print('{} consumed: {}'.format(name, num))
#             time.sleep(random.randint(0, 5))
#         except Empty:
#             pass
#
#     print('Exiting consumer thread', name)
#
#
# def main():
#     q = Queue(10)
#
#     producer = Thread(target=produce, args=(q,))
#     producer.start()
#
#     consumers = []
#     for i in range(3):
#         name = 'Consumer-{}'.format(i)
#         consumer = Thread(target=consume, args=(name, q))
#         consumer.start()
#         consumers.append(consumer)
#
#     producer.join()
#
#     for consumer in consumers:
#         consumer.join()
#
#
# if __name__ == '__main__':
#     main()
#
#
# # ============================================================
#
#
# import threading
# import time
# import logging
# import random
# from queue import Queue
#
# logging.basicConfig(level=logging.DEBUG,
#                     format='(%(threadName)-9s) %(message)s', )
#
# BUF_SIZE = 10
# q = Queue(BUF_SIZE)
#
#
# class ProducerThread(threading.Thread):
#     def __init__(self, group=None, target=None, name=None,
#                  args=(), kwargs=None, verbose=None):
#         super(ProducerThread, self).__init__()
#         self.target = target
#         self.name = name
#
#     def run(self):
#         while True:
#             if not q.full():
#                 item = random.randint(1, 10)
#                 q.put(item)
#                 logging.debug('Putting ' + str(item)
#                               + ' : ' + str(q.qsize()) + ' items in queue')
#                 time.sleep(random.random())
#         return
#
#
# class ConsumerThread(threading.Thread):
#     def __init__(self, group=None, target=None, name=None,
#                  args=(), kwargs=None, verbose=None):
#         super(ConsumerThread, self).__init__()
#         self.target = target
#         self.name = name
#         return
#
#     def run(self):
#         while True:
#             if not q.empty():
#                 item = q.get()
#                 logging.debug('Getting ' + str(item)
#                               + ' : ' + str(q.qsize()) + ' items in queue')
#                 time.sleep(random.random())
#         return
#
#
# if __name__ == '__main__':
#     p = ProducerThread(name='producer')
#     c = ConsumerThread(name='consumer')
#
#     p.start()
#     time.sleep(2)
#     c.start()
#     time.sleep(2)
#
#
# # ============================================================
#
# import multiprocessing
# import time
#
# call_counter = 0
#
#
# def do_work():
#     global call_counter
#     call_counter += 1
#     start_time = time.time()
#     print("Started long operation {}.".format(call_counter))
#     length = 1.0e7
#     sum = 0
#     for i in range(int(length)):
#         sum += i
#
#     print("Long operation {} took {}".format(call_counter, time.time() - start_time))
#
#
# p = multiprocessing.Process(target=do_work)
# p.start()
#
# print("process started")
# print("sleeping for 2 sec.")
#
# time.sleep(2)
#
# print("woke up")
# print("restarting process")
#
# p.start()
#
# print("end")
#
# # ============================================================
# import sys
# import time
#
# from PyQt5 import QtWidgets
# from PyQt5.QtCore import QTimer, QThread, QCoreApplication
#
# call_counter = 0
#
#
# def do_long_operation():
#     global call_counter
#     call_counter += 1
#     start_time = time.time()
#     print("Started long operation {}.".format(call_counter))
#     length = 1.0e7
#     sum = 0
#     for i in range(int(length)):
#         sum += i
#
#     print("Long operation {} took {}".format(call_counter, time.time() - start_time))
#
#
# app = QCoreApplication(sys.argv)
#
# timer = QTimer()
# timer.timeout.connect(do_long_operation)
# timer.start(100)
# print("Timer started.")
#
# app.exec()
#
# # ============================================================
#
# from PyQt5 import QtCore
# from PyQt5.QtCore import QObject
#
#
# class B:
#     def __init__(self, name):
#         self.name = name
#
#
# class A(QObject):
#     sig = QtCore.pyqtSignal(B)
#
#     def __init__(self):
#         super(A, self).__init__()
#         self.sig.connect(self.signal_received)
#
#     def emit_signal(self):
#         b = B("the_cute_b")
#         self.sig.emit(b)
#
#     def signal_received(self, b_instance):
#         print("Received signal with: ", b_instance.name)
#
#
# a = A()
# a.emit_signal()
#
#
# # ============================================================
#
# from tmp_package.tmp1 import A
#
#
# class CheckboxEvent:
#     target_type = A
#
#     def __init__(self):
#         pass
#
#     def fire(self):
#         print("fired ", self)
#
#
# # ============================================================
#
# import sys
#
# from PyQt5.QtWidgets import QApplication, QComboBox
#
#
# def combo_current_index_changed(index, combo_name):
#     print(index)
#     print(combo.itemData(index))
#     print(combo_name)
#
#
# app = QApplication(sys.argv)
# combo = QComboBox()
# combo.addItem("A", object())
# combo.addItem("B", object())
# combo.addItem("C", object())
# combo.currentIndexChanged.connect(lambda index: combo_current_index_changed(index, "ABCCombo"))
# combo.show()
# app.exec()
#
#
# # ============================================================
# from threading import Thread
#
#
# def start_task():
#     t2 = Thread(target=do_task)
#     t2.start()
#
#
# def do_task():
#     j = 0
#     for i in range(30000000):
#         if i == 1000000:
#             print("i is now 1.000.000")
#
#         j += i
#
#     print(j)
#
#
# t1 = Thread(target=start_task)
# t1.start()
#
#
#
# # ============================================================
#
# import threading
# import time
#
#
# class TimerAnnotation:
#     def __init__(self):
#         self.current_time = 0
#         self.duration = 60
#         self.tick_interval = 1
#         self.timer_thread = None
#         self.thread_stop_event = threading.Event()
#
#     def start(self):
#         print("TimerAnnotation: start called")
#         if self.timer_thread is not None:
#             if not self.timer_thread.is_alive():
#                 self.timer_thread.start()
#         else:
#             self.timer_thread = threading.Thread(target=self.tick)
#             self.timer_thread.start()
#
#     def stop(self):
#         print("TimerAnnotation: stop called")
#         self.thread_stop_event.set()
#
#     def reset(self):
#         print("TimerAnnotation: reset called")
#         self.current_time = 0
#         self.thread_stop_event.clear()
#
#     def tick(self):
#         while not self.thread_stop_event.is_set() and \
#                 self.current_time < self.duration:
#             self.current_time += 1
#             if (self.current_time % self.tick_interval) == 0:
#                 print("timer tick")
#
#             time.sleep(1)
#
#         self.timer_thread = None
#         self.thread_stop_event.clear()
#
#
# def stop_timer_annotation(ta):
#     print("Stopping timer annotation")
#     ta.stop()
#
#
# timer_annotation = TimerAnnotation()
# timer_annotation.start()
#
# # threading.Timer(10, stop_timer_annotation, args=(timer_annotation, )).start()
#
# print("waiting for 10 secs, then stopping the timer annotation")
# time.sleep(10)
# stop_timer_annotation(timer_annotation)
#
# print("waiting for 5 secs, then resetting the timer annotation, then restarting timer annotation")
# time.sleep(5)
# timer_annotation.reset()
# timer_annotation.start()
#
#
#
#
#
# # ============================================================
#
# import sys
# from PyQt5 import QtCore, QtWidgets
#
#
# class MyWindow(QtWidgets.QMainWindow):
#     def __init__(self):
#         super().__init__()
#         self.setWindowTitle('MyWindow')
#         self._main = QtWidgets.QWidget()
#         self.setCentralWidget(self._main)
#         self.button = QtWidgets.QPushButton('Do it')
#         self.button.clicked.connect(self.do)
#
#         self.contincheck = QtWidgets.QCheckBox("Continuous")
#         self.contincheck.clicked.connect(self.continuous_doing)
#         self.continuous = False
#         layout = QtWidgets.QGridLayout(self._main)
#         layout.addWidget(self.button, 0, 0)
#         layout.addWidget(self.contincheck, 1, 0)
#
#         self.mythread = MyThread(self.continuous, self)
#         self.mythread.finished.connect(self.thread_finished)
#         self.button.clicked.connect(self.mythread.stop)
#         self.mythread.signal.connect(self.done)
#
#     def continuous_doing(self):
#         self.button.setCheckable(self.contincheck.isChecked())
#         self.continuous = self.contincheck.isChecked()
#
#     def do(self):
#         if self.button.isCheckable() and not self.button.isChecked():
#             self.button.setText('Do it')
#             self.contincheck.setEnabled(True)
#         else:
#             self.mythread.continuous = self.continuous
#             if self.button.isCheckable() and self.button.isChecked():
#                 self.button.setText('Stop doing that')
#                 self.contincheck.setDisabled(True)
#
#             self.mythread.start()
#
#     @QtCore.pyqtSlot(int)
#     def done(self, i):
#         print('done it', i)
#
#     @QtCore.pyqtSlot()
#     def thread_finished(self):
#         print('thread finished')
#
#
# class MyThread(QtCore.QThread):
#     signal = QtCore.pyqtSignal(int)
#
#     def __init__(self, continuous=False, parent=None):
#         super(MyThread, self).__init__(parent)
#         self._stopped = True
#         self.continuous = continuous
#         self.i = 0
#
#     def __del__(self):
#         self.wait()
#
#     def stop(self):
#         self._stopped = True
#
#     def run(self):
#         self._stopped = False
#         while True:
#             self.signal.emit(self.i)
#             if self._stopped:
#                 break
#             if self.continuous:
#                 QtCore.QThread.sleep(2)
#             else:
#                 break
#
#
# if __name__ == '__main__':
#     app = QtCore.QCoreApplication.instance()
#     if app is None:
#         app = QtWidgets.QApplication(sys.argv)
#     mainGui = MyWindow()
#     mainGui.show()
#     app.aboutToQuit.connect(app.deleteLater)
#     app.exec_()
#
#
# # ============================================================================
#
# a = True
# b = False
# c = a is True
# d = b is False
#
# print(c, d)
#
#
# # ============================================================================
#
# class MyClass:
#     def __init__(self):
#         self.position = (1, 1)
#
#
# my_obj = MyClass()
# print(my_obj.position)
#
# my_obj.poison = (10, 10)
# print(my_obj.poison)
#
#
# # ============================================================================
#
# import cv2
# import numpy as np
#
#
# a = np.array([2])
# print(a)
# print(a == 2)
# print(a.squeeze())
#
#
#
# def tmp_package():
#    v1_marker = np.array([[447., 117.],
#        [501.,  115.],
#        [502.,  169.],
#        [448., 171.]])
#
#    v2_marker = np.array([[1474.,  800.],
#        [1530.,  797.],
#        [1535., 853.],
#        [1477., 858.]])
#
#    cam_proj_homography = np.array([[ 9.39041649e-01, -1.15517376e-03, -2.42452010e+02],
#        [ 2.27973037e-02,  9.66755076e-01, -8.65972180e+01],
#        [-2.12478066e-05,  4.18114680e-05,  1.00000000e+00]])
#
#    v1_marker_normalized = v1_marker - v1_marker[0]
#    v2_marker_normalized = v2_marker - v1_marker[0]
#
#    v1_marker_p = cv2.perspectiveTransform(np.array([v1_marker]), cam_proj_homography).squeeze()
#    v2_marker_p = cv2.perspectiveTransform(np.array([v2_marker]), cam_proj_homography).squeeze()
#
#    v1_marker_p_normalized = v1_marker_p - v1_marker_p[0]
#    v2_marker_p_normalized = v2_marker_p - v1_marker_p[0]
#
#    camera_points = np.vstack((v1_marker_normalized, v2_marker_normalized))
#    projector_points = np.vstack((v1_marker_p_normalized, v2_marker_p_normalized))
#
#    print(camera_points.shape)
#    print(projector_points.shape)
#
#    scene_homography, _ = cv2.findHomography(np.array([camera_points]), np.array([projector_points]), cv2.RANSAC, 3)
#
#    # scene_homography, _ = cv2.findHomography(
#    #  np.array([camera_points]).squeeze(), np.array([projector_points]).squeeze(), cv2.RANSAC, 3)
#
#
#    # print(v1_marker_normalized)
#    # print(v2_marker_normalized)
#    #
#    print(scene_homography)
#
#
#
# # ============================================================================
#
# class MyClass:
#     def a_method(self):
#         print("MyClass.a_method()")
#
#
# def a_method():
#     pass
#
#
# # ============================================================================
#
# phys_obj_predictions = {}
#
# phys_obj_predictions["tmp_package"] = [1, 2, 3]
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
# d.append(12)
# # d.append("adfa") # TypeError: an integer is required (got type str)
#
# print(b)
# print(c)
# print(type(c))
# print(d)
# print(type(d))
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
