import random
import sys
from PyQt5 import QtWidgets, uic, QtCore, QtGui


class Worker(QtCore.QThread):
    data = QtCore.pyqtSignal(dict)

    def __init__(self, parent=None):
        super(Worker, self).__init__(parent)
        self._stopped = True
        self._mutex = QtCore.QMutex()

    def stop(self):
        self._mutex.lock()
        self._stopped = True
        self._mutex.unlock()

    def run(self):
        self._stopped = False
        for count in range(1000):
            if self._stopped:
                break
            self.msleep(50)
            data = {
                'message': 'running %d [%d]' % (
                    count, QtCore.QThread.currentThreadId()),
                'time': QtCore.QTime.currentTime(),
                'items': [1, 2, 3],
                'progress': random.randrange(101)
            }
            self.data.emit(data)


class HyperScanApp(QtWidgets.QMainWindow):
    _serial_connected = False
    _serial_connecting = False
    _current_serial_ports = None
    _start_scan = False

    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)

        self._worker = Worker()
        self._worker.started.connect(self.worker_started_callback)
        self._worker.finished.connect(self.worker_finished_callback)
        self._worker.data.connect(self.worker_data_callback)

        self.ui = uic.loadUi('progress_bar.ui', self)
        self.ui.progressBar.setValue(random.randrange(101))
        self.ui.show()
        self._worker.start()

    def worker_started_callback(self):
        pass

    def worker_finished_callback(self):
        pass

    def worker_data_callback(self, data):
        self.ui.progressBar.setValue(data['progress'])
        print(data['progress'])


def main():
    app = QtWidgets.QApplication(sys.argv)
    HyperScanApp()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()



# # ====================================================================================
#
# import sys
# import random
#
# from PyQt5 import QtCore, QtGui
#
#
# class Example(QtCore.QObject):
#
#     signalStatus = QtCore.pyqtSignal(str)
#
#     def __init__(self, parent=None):
#         super(self.__class__, self).__init__(parent)
#
#         # Create a gui object.
#         self.gui = Window()
#
#         # Create a new worker thread.
#         self.createWorkerThread()
#
#         # Make any cross object connections.
#         self._connectSignals()
#
#         self.gui.show()
#
#     def _connectSignals(self):
#         self.gui.button_cancel.clicked.connect(self.forceWorkerReset)
#         self.signalStatus.connect(self.gui.updateStatus)
#         self.parent().aboutToQuit.connect(self.forceWorkerQuit)
#
#     def createWorkerThread(self):
#         # Setup the worker object and the worker_thread.
#         self.worker = WorkerObject()
#         self.worker_thread = QtCore.QThread()
#         self.worker.moveToThread(self.worker_thread)
#         self.worker_thread.start()
#
#         # Connect any worker signals
#         self.worker.signalStatus.connect(self.gui.updateStatus)
#         self.gui.button_start.clicked.connect(self.worker.startWork)
#
#     def forceWorkerReset(self):
#         if self.worker_thread.isRunning():
#             print('Terminating thread.')
#             self.worker_thread.terminate()
#
#             print('Waiting for thread termination.')
#             self.worker_thread.wait()
#
#             self.signalStatus.emit('Idle.')
#
#             print('building new working object.')
#             self.createWorkerThread()
#
#     def forceWorkerQuit(self):
#         if self.worker_thread.isRunning():
#             self.worker_thread.terminate()
#             self.worker_thread.wait()
#
#
# class WorkerObject(QtCore.QObject):
#
#     signalStatus = QtCore.pyqtSignal(str)
#
#     def __init__(self, parent=None):
#         super(self.__class__, self).__init__(parent)
#
#     @QtCore.pyqtSlot()
#     def startWork(self):
#         for ii in range(7):
#             number = random.randint(0,5000**ii)
#             self.signalStatus.emit('Iteration: {}, Factoring: {}'.format(ii, number))
#             factors = self.primeFactors(number)
#             print('Number: ', number, 'Factors: ', factors)
#         self.signalStatus.emit('Idle.')
#
#     def primeFactors(self, n):
#         i = 2
#         factors = []
#         while i * i <= n:
#             if n % i:
#                 i += 1
#             else:
#                 n //= i
#                 factors.append(i)
#         if n > 1:
#             factors.append(n)
#         return factors
#
#
# class Window(QtGui.QWidget):
#
#     def __init__(self):
#         QtGui.QWidget.__init__(self)
#         self.button_start = QtGui.QPushButton('Start', self)
#         self.button_cancel = QtGui.QPushButton('Cancel', self)
#         self.label_status = QtGui.QLabel('', self)
#
#         layout = QtGui.QVBoxLayout(self)
#         layout.addWidget(self.button_start)
#         layout.addWidget(self.button_cancel)
#         layout.addWidget(self.label_status)
#
#         self.setFixedSize(400, 200)
#
#     @QtCore.pyqtSlot(str)
#     def updateStatus(self, status):
#         self.label_status.setText(status)
#
#
# if __name__=='__main__':
#     app = QtGui.QApplication(sys.argv)
#     example = Example(app)
#     sys.exit(app.exec_())