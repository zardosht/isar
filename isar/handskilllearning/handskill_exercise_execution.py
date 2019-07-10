import logging
import os

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QMainWindow, QFileDialog

from isar.camera.camera import CameraService
from isar.handskilllearning.handskill_exercise_model import FollowThePathExercise, CatchTheObjectExercise
from isar.projection.projector import ProjectorView
from isar.scene import scenemodel
from isar.scene.annotationmodel import AnnotationsModel, TimerAnnotation, CounterAnnotation
from isar.scene.physicalobjectmodel import PhysicalObjectsModel
from isar.scene.scenemodel import ScenesModel
from isar.services import servicemanager
from isar.services.servicemanager import ServiceNames

logger = logging.getLogger("isar.handskill_exercise_execution")


class HandSkillExerciseExecution(QMainWindow):

    def __init__(self, screen_id):
        super().__init__()
        self.setup_ui(self)
        self.setup_signals()
        self.setup_constraints()
        self.setWindowTitle("Handskill Exercise Execution")
        self.exercise = None
        self._projector_view_timer = None

        self._camera_service: CameraService = None
        self.setup_camera_service()

        self.projector_view = None
        self.projector_initialized = self.setup_projector_view(screen_id)
        if not self.projector_initialized:
            logger.error("Projector is not ready! Return")
            return

        self._selection_stick_service = None
        self.setup_object_detection_service()

        self.scenes_model = None
        self.annotations_model = None
        self.physical_objects_model = None
        self.setup_models()

        self.setAttribute(QtCore.Qt.WA_QuitOnClose, True)

    def setup_signals(self):
        self.button_calibrate_projector.clicked.connect(self.calibrate_projector)
        self.button_init_scene_size.clicked.connect(self.init_scene_size)
        self.button_load_project.clicked.connect(self.load_project)
        self.button_select_exercise.clicked.connect(self.select_exercise)
        self.button_start.clicked.connect(self.start_exercise)

    def setup_camera_service(self):
        self._camera_service = servicemanager.get_service(ServiceNames.CAMERA1)
        self._camera_service.start_capture()

    def setup_projector_view(self, screen_id):
        self.projector_view = ProjectorView(self.projector_view, screen_id, self._camera_service)
        if self.projector_view.is_projector_ready():
            self.projector_view.setWindowFlag(QtCore.Qt.Window)
            self.calibrate_projector()
            return True
        else:
            logger.error("Could not initialize projector. Make sure projector is connected and is turned on!")
            return False

    def setup_object_detection_service(self):
        self._selection_stick_service = servicemanager.get_service(ServiceNames.SELECTION_STICK)

    def setup_models(self):
        self.scenes_model = ScenesModel()
        self.annotations_model = AnnotationsModel()
        self.physical_objects_model = PhysicalObjectsModel()

        self.scenes_model.scene_changed.connect(self.current_scene_changed)

    def current_scene_changed(self):
        self.annotations_model.set_scene(self.scenes_model.get_current_scene())
        self.physical_objects_model.set_scene(self.scenes_model.get_current_scene())
        self.projector_view.set_annotations_model(self.annotations_model)

        servicemanager.current_scene_changed(self.scenes_model.get_current_scene())

    def calibrate_projector(self):
        self.projector_view.calibrating = True
        self.projector_view.calibrate_projector()

    def init_scene_size(self):
        self.projector_view.init_scene_size()
        self.button_load_project.setEnabled(True)

    def load_project(self):
        project_filename = QFileDialog.getOpenFileName(filter="(*.json)")[0]
        project_dir = os.path.dirname(project_filename)
        project_name = os.path.splitext(os.path.basename(project_filename))[0]
        if project_dir is None or project_dir == "":
            return

        self.line_project_name.setText(project_name)
        self.scenes_model.load_project(project_dir, project_name)

        model = QStandardItemModel()
        for exercise in scenemodel.current_project.exercises:
            if self.radio_button_follow.isChecked() and isinstance(exercise, FollowThePathExercise):
                item = QStandardItem()
                item.setText(exercise.name)
                model.appendRow(item)

            if self.radio_button_catch.isChecked() and isinstance(exercise, CatchTheObjectExercise):
                item = QStandardItem()
                item.setText(exercise.name)
                model.appendRow(item)

        self.list_exercises.setModel(model)
        self.radio_button_follow.setEnabled(False)
        self.radio_button_catch.setEnabled(False)

    def select_exercise(self):
        index = self.list_exercises.currentIndex()
        selected = index.data()
        self.line_selected_exercises.setText(selected)
        for exercise_object in scenemodel.current_project.exercises:
            if exercise_object.name == selected:
                self.exercise = exercise_object
        self.button_start.setEnabled(True)

    def start_exercise(self):
        current_scene = self.exercise.scene

        # TODO: Fix me (find a proper place to configure the service).
        rules_service = servicemanager.get_service(ServiceNames.RULES_SERVICE)
        rules_service.set_current_scene(current_scene)

        self.annotations_model.set_scene(current_scene)
        self.projector_view.set_annotations_model(self.annotations_model)

        # check which radio button is checked and set the duration and feedback target value
        timers = current_scene.get_all_annotations_by_type(TimerAnnotation)
        if self.radio_button_beginner.isChecked():
            timers[0].duration.set_value(self.exercise.time.beginner.get_value())
            if self.radio_button_follow.isChecked():
                self.exercise.feedback.set_target_value(self.exercise.error.beginner.get_value())
            if self.radio_button_catch.isChecked():
                self.exercise.feedback.set_target_value(self.exercise.number.beginner.get_value())

        if self.radio_button_intermediate.isChecked():
            timers[0].duration.set_value(self.exercise.time.intermediate.get_value())
            if self.radio_button_follow.isChecked():
                self.exercise.feedback.set_target_value(self.exercise.error.intermediate.get_value())
            if self.radio_button_catch.isChecked():
                self.exercise.feedback.set_target_value(self.exercise.number.intermediate.get_value())

        if self.radio_button_competent.isChecked():
            timers[0].duration.set_value(self.exercise.time.competent.get_value())
            if self.radio_button_follow.isChecked():
                self.exercise.feedback.set_target_value(self.exercise.error.competent.get_value())
            if self.radio_button_catch.isChecked():
                self.exercise.feedback.set_target_value(self.exercise.number.competent.get_value())

        counters = current_scene.get_all_annotations_by_type(CounterAnnotation)
        if len(counters) > 0:
            self.exercise.hasCounterAnnotation = True
            counters[0].target_number.set_value(self.exercise.feedback.target_value)

        self._selection_stick_service.set_annotations_model(self.annotations_model)
        self._selection_stick_service.set_physical_objects_model(self.physical_objects_model)
        self.exercise.selection_stick = self._selection_stick_service
        self.setup_timers()

    def setup_timers(self):
        self._projector_view_timer = QTimer()
        self._projector_view_timer.timeout.connect(self.update_projector_view)
        self._projector_view_timer.start(5)

    def update_projector_view(self):
        if self.projector_view.calibrating:
            return
        else:
            camera_frame = self._camera_service.get_frame()
            if camera_frame is None:
                return

            self.projector_view.update_projector_view(camera_frame)

    def close(self):
        self._projector_view_timer.stop()
        self.projector_view.close()
        super().close()

    # Just to get the other window (the projector widget) to close :/
    def closeEvent(self, event):
        self.projector_view.close()
        super().closeEvent(event)

    def setup_constraints(self):
        self.radio_button_follow.setChecked(True)
        self.button_load_project.setEnabled(False)
        self.line_project_name.setEnabled(False)
        self.line_selected_exercises.setEnabled(False)
        self.radio_button_beginner.setChecked(True)
        self.button_start.setEnabled(False)

    def setup_ui(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(400, 550)

        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.button_calibrate_projector = QtWidgets.QPushButton(self.centralwidget)
        self.button_calibrate_projector.setObjectName("button_calibrate_projector")
        self.horizontalLayout_3.addWidget(self.button_calibrate_projector)
        self.button_init_scene_size = QtWidgets.QPushButton(self.centralwidget)
        self.button_init_scene_size.setObjectName("button_init_scene_size")
        self.horizontalLayout_3.addWidget(self.button_init_scene_size)
        self.gridLayout.addLayout(self.horizontalLayout_3, 0, 0, 1, 3)
        self.label_exercise_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_exercise_2.setObjectName("label_exercise_2")
        self.gridLayout.addWidget(self.label_exercise_2, 1, 0, 1, 1)
        self.exercise_typ_box = QtWidgets.QGroupBox(self.centralwidget)
        self.exercise_typ_box.setObjectName("exercise_typ_box")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.exercise_typ_box)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.radio_button_follow = QtWidgets.QRadioButton(self.exercise_typ_box)
        self.radio_button_follow.setObjectName("radio_button_follow")
        self.horizontalLayout.addWidget(self.radio_button_follow)
        self.radio_button_catch = QtWidgets.QRadioButton(self.exercise_typ_box)
        self.radio_button_catch.setObjectName("radio_button_catch")
        self.horizontalLayout.addWidget(self.radio_button_catch)
        self.gridLayout.addWidget(self.exercise_typ_box, 1, 1, 1, 2)
        self.label_project_name = QtWidgets.QLabel(self.centralwidget)
        self.label_project_name.setObjectName("label_project_name")
        self.gridLayout.addWidget(self.label_project_name, 2, 0, 1, 1)
        self.line_project_name = QtWidgets.QLineEdit(self.centralwidget)
        self.line_project_name.setObjectName("line_project_name")
        self.gridLayout.addWidget(self.line_project_name, 2, 1, 1, 1)
        self.button_load_project = QtWidgets.QPushButton(self.centralwidget)
        self.button_load_project.setObjectName("button_load_project")
        self.gridLayout.addWidget(self.button_load_project, 2, 2, 1, 1)
        self.label_exercise = QtWidgets.QLabel(self.centralwidget)
        self.label_exercise.setObjectName("label_exercise")
        self.gridLayout.addWidget(self.label_exercise, 3, 0, 1, 1)
        self.list_exercises = QtWidgets.QListView(self.centralwidget)
        self.list_exercises.setObjectName("list_exercises")
        self.gridLayout.addWidget(self.list_exercises, 3, 1, 1, 2)
        self.label_selected = QtWidgets.QLabel(self.centralwidget)
        self.label_selected.setObjectName("label_selected")
        self.gridLayout.addWidget(self.label_selected, 4, 0, 1, 1)
        self.line_selected_exercises = QtWidgets.QLineEdit(self.centralwidget)
        self.line_selected_exercises.setObjectName("line_selected_exercises")
        self.gridLayout.addWidget(self.line_selected_exercises, 4, 1, 1, 1)
        self.button_select_exercise = QtWidgets.QPushButton(self.centralwidget)
        self.button_select_exercise.setObjectName("button_select_exercise")
        self.gridLayout.addWidget(self.button_select_exercise, 4, 2, 1, 1)
        self.label_skill_level = QtWidgets.QLabel(self.centralwidget)
        self.label_skill_level.setObjectName("label_skill_level")
        self.gridLayout.addWidget(self.label_skill_level, 5, 0, 1, 1)
        self.group_skill_level = QtWidgets.QGroupBox(self.centralwidget)
        self.group_skill_level.setObjectName("group_skill_level")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.group_skill_level)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.radio_button_beginner = QtWidgets.QRadioButton(self.group_skill_level)
        self.radio_button_beginner.setObjectName("radio_button_beginner")
        self.horizontalLayout_2.addWidget(self.radio_button_beginner)
        self.radio_button_intermediate = QtWidgets.QRadioButton(self.group_skill_level)
        self.radio_button_intermediate.setObjectName("radio_button_intermediate")
        self.horizontalLayout_2.addWidget(self.radio_button_intermediate)
        self.radio_button_competent = QtWidgets.QRadioButton(self.group_skill_level)
        self.radio_button_competent.setObjectName("radio_button_competent")
        self.horizontalLayout_2.addWidget(self.radio_button_competent)
        self.gridLayout.addWidget(self.group_skill_level, 5, 1, 1, 2)
        self.button_start = QtWidgets.QPushButton(self.centralwidget)
        self.button_start.setObjectName("button_start")
        self.gridLayout.addWidget(self.button_start, 6, 1, 1, 2)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 286, 17))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslate_ui(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslate_ui(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.button_calibrate_projector.setText(_translate("MainWindow", "Calibrate Projector"))
        self.button_init_scene_size.setText(_translate("MainWindow", "Init Scene Size"))
        self.label_exercise_2.setText(_translate("MainWindow", "Exercise type:"))
        self.radio_button_follow.setText(_translate("MainWindow", "Follow The Path"))
        self.radio_button_catch.setText(_translate("MainWindow", "Catch The Object"))
        self.label_project_name.setText(_translate("MainWindow", "Project name:"))
        self.button_load_project.setText(_translate("MainWindow", "Load project"))
        self.label_exercise.setText(_translate("MainWindow", "Exercise:"))
        self.label_selected.setText(_translate("MainWindow", "Selected exercise:"))
        self.button_select_exercise.setText(_translate("MainWindow", "Select"))
        self.label_skill_level.setText(_translate("MainWindow", "Skill level:"))
        self.radio_button_beginner.setText(_translate("MainWindow", "Beginner"))
        self.radio_button_intermediate.setText(_translate("MainWindow", "Intermediate"))
        self.radio_button_competent.setText(_translate("MainWindow", "Competent"))
        self.button_start.setText(_translate("MainWindow", "Start"))
