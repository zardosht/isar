import os

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import QIntValidator, QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QWizard, QFileDialog

from isar.handskilllearning.handskill_exercise_model import FollowThePathExercise
from isar.scene import scenemodel
from isar.scene.annotationmodel import CurveAnnotation
from isar.scene.scenemodel import ScenesModel


class HandSkillExerciseDefinition(QWizard):

    def __init__(self):
        super().__init__()
        self.exercise = FollowThePathExercise()
        self.scenes_model = None

        self.setup_ui(self)
        self.setup_signals()
        self.setup_constraints()
        self.setup_models()

        self.setWindowTitle("Follow the path exercise")

    def setup_signals(self):
        self.button_load_project.clicked.connect(self.load_project)
        self.button_select_scene.clicked.connect(self.select_scene)
        self.button(QWizard.FinishButton).clicked.connect(self.finish_clicked)

    def setup_models(self):
        self.scenes_model = ScenesModel()

    def load_project(self):
        project_filename = QFileDialog.getOpenFileName(filter="(*.json)")[0]
        project_dir = os.path.dirname(project_filename)
        project_name = os.path.splitext(os.path.basename(project_filename))[0]
        if project_dir is None or project_dir == "":
            return
        self.line_project_name.setText(project_name)
        self.button_select_scene.setEnabled(True)

        self.scenes_model.load_project(project_dir, project_name)
        model = QStandardItemModel()
        for scene in self.scenes_model.get_all_scenes():
            count = 0
            for annotation in scene.get_all_annotations():
                if isinstance(annotation, CurveAnnotation):
                    count = count + 1
            if count == 1:
                item = QStandardItem()
                item.setText(scene.name)
                model.appendRow(item)
        self.list_scenes.setModel(model)

    def select_scene(self):
        index = self.list_scenes.currentIndex()
        selected = index.data()
        self.line_selected_scenes.setText(selected)
        for scene in self.scenes_model.get_all_scenes():
            if scene.name == selected:
                self.exercise.set_scene(scene)
        for annotation in self.exercise.scene.get_all_annotations():
            if isinstance(annotation, CurveAnnotation):
                self.line_number_points.setText(str(annotation.points.get_value()))

    def finish_clicked(self):
        self.save_info_target_values()
        self.save_info_feedback()
        self.save_exercise()

    def save_info_target_values(self):
        self.exercise.error.beginner.set_value(int(self.line_error_beg.text()))
        self.exercise.time.beginner.set_value(int(self.line_time_beg.text()))

        self.exercise.error.intermediate.set_value(int(self.line_error_int.text()))
        self.exercise.time.intermediate.set_value(int(self.line_time_int.text()))

        self.exercise.error.competent.set_value(int(self.line_error_com.text()))
        self.exercise.time.competent.set_value(int(self.line_time_com.text()))

    def save_info_feedback(self):
        self.exercise.feedback.set_good((int(self.line_good.text())))
        self.exercise.feedback.set_average((int(self.line_average.text())))
        self.exercise.feedback.set_bad((int(self.line_bad.text())))

    def save_exercise(self):
        parent_dir = None
        project_name = None
        if not scenemodel.current_project:
            parent_dir = QFileDialog.getExistingDirectory()
            if parent_dir is None or parent_dir == "":
                return
            project_name = self.project_name_le.text()

        self.exercise.name = self.line_exercise_name.text()
        scenemodel.current_project.exercises.append(self.exercise)
        self.scenes_model.save_project(parent_dir, project_name)

    # TODO: fix register field for different feedback
    def setup_constraints(self):
        # register fields to enable/disable the next/finish button
        self.scene.registerField("line_selected_scenes*", self.line_selected_scenes)
        self.target_value.registerField("line_error_beg*", self.line_error_beg)
        self.target_value.registerField("line_time_beg*", self.line_time_beg)
        self.target_value.registerField("line_error_int*", self.line_error_int)
        self.target_value.registerField("line_time_int*", self.line_time_int)
        self.target_value.registerField("line_error_com*", self.line_error_com)
        self.target_value.registerField("line_time_com*", self.line_time_com)
        self.target_value.registerField("line_number_points*", self.line_number_points)
        self.feedback.registerField("line_good*", self.line_good)
        self.feedback.registerField("line_average*", self.line_average)
        self.feedback.registerField("line_bad*", self.line_bad)
        self.feedback.registerField("line_exercise_name*", self.line_exercise_name)

        # set the line edit content to be a number
        self.line_error_beg.setValidator(QIntValidator())
        self.line_time_beg.setValidator(QIntValidator())
        self.line_error_int.setValidator(QIntValidator())
        self.line_time_int.setValidator(QIntValidator())
        self.line_error_com.setValidator(QIntValidator())
        self.line_time_com.setValidator(QIntValidator())
        self.line_good.setValidator(QIntValidator())
        self.line_average.setValidator(QIntValidator())
        self.line_bad.setValidator(QIntValidator())

        self.line_project_name.setEnabled(False)
        self.line_selected_scenes.setEnabled(False)
        self.button_select_scene.setEnabled(False)
        self.line_number_points.setEnabled(False)

    def setup_ui(self, Wizard):
        Wizard.setObjectName("Wizard")
        Wizard.resize(400, 400)
        self.setWizardStyle(QWizard.WizardStyle.ModernStyle)
        self.setButtonText(QWizard.FinishButton, "&Save and Finish")

        self.scene = QtWidgets.QWizardPage()
        self.scene.setObjectName("scene")
        self.gridLayout = QtWidgets.QGridLayout(self.scene)
        self.gridLayout.setObjectName("gridLayout")
        self.button_load_project = QtWidgets.QPushButton(self.scene)
        self.button_load_project.setObjectName("button_load_project")
        self.gridLayout.addWidget(self.button_load_project, 0, 3, 1, 1)
        self.line_project_name = QtWidgets.QLineEdit(self.scene)
        self.line_project_name.setObjectName("line_project_name")
        self.gridLayout.addWidget(self.line_project_name, 0, 2, 1, 1)
        self.label_selected = QtWidgets.QLabel(self.scene)
        self.label_selected.setObjectName("label_selected")
        self.gridLayout.addWidget(self.label_selected, 4, 0, 1, 2)
        self.label_project_name = QtWidgets.QLabel(self.scene)
        self.label_project_name.setObjectName("label_project_name")
        self.gridLayout.addWidget(self.label_project_name, 0, 0, 1, 2)
        self.list_scenes = QtWidgets.QListView(self.scene)
        self.list_scenes.setObjectName("list_scenes")
        self.gridLayout.addWidget(self.list_scenes, 1, 1, 1, 3)
        self.label_scenes = QtWidgets.QLabel(self.scene)
        self.label_scenes.setObjectName("label_scenes")
        self.gridLayout.addWidget(self.label_scenes, 1, 0, 1, 1)
        self.line_selected_scenes = QtWidgets.QLineEdit(self.scene)
        self.line_selected_scenes.setObjectName("line_selected_scenes")
        self.gridLayout.addWidget(self.line_selected_scenes, 4, 2, 1, 1)
        self.button_select_scene = QtWidgets.QPushButton(self.scene)
        self.button_select_scene.setObjectName("button_select_scene")
        self.gridLayout.addWidget(self.button_select_scene, 4, 3, 1, 1)
        Wizard.addPage(self.scene)

        self.target_value = QtWidgets.QWizardPage()
        self.target_value.setObjectName("target_value")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.target_value)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.label_number_points = QtWidgets.QLabel(self.target_value)
        self.label_number_points.setObjectName("label_number_points")
        self.gridLayout_2.addWidget(self.label_number_points, 0, 0, 1, 2)
        self.line_number_points = QtWidgets.QLineEdit(self.target_value)
        self.line_number_points.setObjectName("line_number_points")
        self.gridLayout_2.addWidget(self.line_number_points, 0, 2, 1, 2)
        self.label_skill_level = QtWidgets.QLabel(self.target_value)
        self.label_skill_level.setObjectName("label_skill_level")
        self.gridLayout_2.addWidget(self.label_skill_level, 1, 0, 1, 2)
        self.label_error = QtWidgets.QLabel(self.target_value)
        self.label_error.setObjectName("label_error")
        self.gridLayout_2.addWidget(self.label_error, 2, 0, 1, 1)
        self.line_error_beg = QtWidgets.QLineEdit(self.target_value)
        self.line_error_beg.setObjectName("line_error_beg")
        self.gridLayout_2.addWidget(self.line_error_beg, 2, 1, 1, 2)
        self.label_time = QtWidgets.QLabel(self.target_value)
        self.label_time.setObjectName("label_time")
        self.gridLayout_2.addWidget(self.label_time, 2, 3, 1, 1)
        self.line_time_beg = QtWidgets.QLineEdit(self.target_value)
        self.line_time_beg.setObjectName("line_time_beg")
        self.gridLayout_2.addWidget(self.line_time_beg, 2, 4, 1, 1)
        self.label_skill_level_2 = QtWidgets.QLabel(self.target_value)
        self.label_skill_level_2.setObjectName("label_skill_level_2")
        self.gridLayout_2.addWidget(self.label_skill_level_2, 3, 0, 1, 3)
        self.label_error_2 = QtWidgets.QLabel(self.target_value)
        self.label_error_2.setObjectName("label_error_2")
        self.gridLayout_2.addWidget(self.label_error_2, 4, 0, 1, 1)
        self.line_error_int = QtWidgets.QLineEdit(self.target_value)
        self.line_error_int.setObjectName("line_error_int")
        self.gridLayout_2.addWidget(self.line_error_int, 4, 1, 1, 2)
        self.label_time_2 = QtWidgets.QLabel(self.target_value)
        self.label_time_2.setObjectName("label_time_2")
        self.gridLayout_2.addWidget(self.label_time_2, 4, 3, 1, 1)
        self.line_time_int = QtWidgets.QLineEdit(self.target_value)
        self.line_time_int.setObjectName("line_time_int")
        self.gridLayout_2.addWidget(self.line_time_int, 4, 4, 1, 1)
        self.label_skill_level_3 = QtWidgets.QLabel(self.target_value)
        self.label_skill_level_3.setObjectName("label_skill_level_3")
        self.gridLayout_2.addWidget(self.label_skill_level_3, 5, 0, 1, 3)
        self.label_error_3 = QtWidgets.QLabel(self.target_value)
        self.label_error_3.setObjectName("label_error_3")
        self.gridLayout_2.addWidget(self.label_error_3, 6, 0, 1, 1)
        self.line_error_com = QtWidgets.QLineEdit(self.target_value)
        self.line_error_com.setObjectName("line_error_com")
        self.gridLayout_2.addWidget(self.line_error_com, 6, 1, 1, 2)
        self.label_time_3 = QtWidgets.QLabel(self.target_value)
        self.label_time_3.setObjectName("label_time_3")
        self.gridLayout_2.addWidget(self.label_time_3, 6, 3, 1, 1)
        self.line_time_com = QtWidgets.QLineEdit(self.target_value)
        self.line_time_com.setObjectName("line_time_com")
        self.gridLayout_2.addWidget(self.line_time_com, 6, 4, 1, 1)
        Wizard.addPage(self.target_value)

        self.feedback = QtWidgets.QWizardPage()
        self.feedback.setObjectName("feedback")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.feedback)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.label_good = QtWidgets.QLabel(self.feedback)
        self.label_good.setObjectName("label_good")
        self.gridLayout_3.addWidget(self.label_good, 0, 0, 1, 1)
        self.line_good = QtWidgets.QLineEdit(self.feedback)
        self.line_good.setObjectName("line_good")
        self.gridLayout_3.addWidget(self.line_good, 0, 1, 1, 1)
        self.label_prozent_1 = QtWidgets.QLabel(self.feedback)
        self.label_prozent_1.setObjectName("label_prozent_1")
        self.gridLayout_3.addWidget(self.label_prozent_1, 0, 2, 1, 1)
        self.label_average = QtWidgets.QLabel(self.feedback)
        self.label_average.setObjectName("label_average")
        self.gridLayout_3.addWidget(self.label_average, 1, 0, 1, 1)
        self.line_average = QtWidgets.QLineEdit(self.feedback)
        self.line_average.setObjectName("line_average")
        self.gridLayout_3.addWidget(self.line_average, 1, 1, 1, 1)
        self.label_prozent_2 = QtWidgets.QLabel(self.feedback)
        self.label_prozent_2.setObjectName("label_prozent_2")
        self.gridLayout_3.addWidget(self.label_prozent_2, 1, 2, 1, 1)
        self.label_bad = QtWidgets.QLabel(self.feedback)
        self.label_bad.setObjectName("label_bad")
        self.gridLayout_3.addWidget(self.label_bad, 2, 0, 1, 1)
        self.line_bad = QtWidgets.QLineEdit(self.feedback)
        self.line_bad.setObjectName("line_bad")
        self.gridLayout_3.addWidget(self.line_bad, 2, 1, 1, 1)
        self.label_prozent_3 = QtWidgets.QLabel(self.feedback)
        self.label_prozent_3.setObjectName("label_prozent_3")
        self.gridLayout_3.addWidget(self.label_prozent_3, 2, 2, 1, 1)
        self.label_exercise_name = QtWidgets.QLabel(self.feedback)
        self.label_exercise_name.setObjectName("label_exercise_name")
        self.gridLayout_3.addWidget(self.label_exercise_name, 3, 0, 1, 1)
        self.line_exercise_name = QtWidgets.QLineEdit(self.feedback)
        self.line_exercise_name.setObjectName("line_exercise_name")
        self.gridLayout_3.addWidget(self.line_exercise_name, 4, 0, 1, 1)
        Wizard.addPage(self.feedback)

        self.retranslate_ui(Wizard)
        QtCore.QMetaObject.connectSlotsByName(Wizard)
        Wizard.setTabOrder(self.button_load_project, self.line_project_name)
        Wizard.setTabOrder(self.line_project_name, self.list_scenes)
        Wizard.setTabOrder(self.list_scenes, self.line_selected_scenes)
        Wizard.setTabOrder(self.line_selected_scenes, self.line_error_beg)
        Wizard.setTabOrder(self.line_error_beg, self.line_time_beg)
        Wizard.setTabOrder(self.line_time_beg, self.line_error_int)
        Wizard.setTabOrder(self.line_error_int, self.line_time_int)
        Wizard.setTabOrder(self.line_time_int, self.line_error_com)
        Wizard.setTabOrder(self.line_error_com, self.line_time_com)
        Wizard.setTabOrder(self.line_time_com, self.line_good)
        Wizard.setTabOrder(self.line_good, self.line_average)
        Wizard.setTabOrder(self.line_average, self.line_bad)
        Wizard.setTabOrder(self.line_bad, self.line_exercise_name)

    def retranslate_ui(self, Wizard):
        _translate = QtCore.QCoreApplication.translate
        Wizard.setWindowTitle(_translate("Wizard", "Wizard"))
        self.button_load_project.setText(_translate("Wizard", "Load project"))
        self.label_selected.setText(_translate("Wizard", "Selected scene:"))
        self.label_project_name.setText(_translate("Wizard", "Project name:"))
        self.label_scenes.setText(_translate("Wizard", "Scenes:"))
        self.button_select_scene.setText(_translate("Wizard", "Select"))
        self.label_number_points.setText(_translate("Wizard", "Number of points:"))
        self.label_skill_level.setText(_translate("Wizard", "Skill level beginner:"))
        self.label_error.setText(_translate("Wizard", "Error:"))
        self.label_time.setText(_translate("Wizard", "Time:"))
        self.label_skill_level_2.setText(_translate("Wizard", "Skill level intermediate:"))
        self.label_error_2.setText(_translate("Wizard", "Error:"))
        self.label_time_2.setText(_translate("Wizard", "Time:"))
        self.label_skill_level_3.setText(_translate("Wizard", "Skill level competent:"))
        self.label_error_3.setText(_translate("Wizard", "Error:"))
        self.label_time_3.setText(_translate("Wizard", "Time:"))
        self.label_good.setText(_translate("Wizard", "Good min number points:"))
        self.label_prozent_1.setText(_translate("Wizard", "%"))
        self.label_average.setText(_translate("Wizard", "Average min number points:"))
        self.label_prozent_2.setText(_translate("Wizard", "%"))
        self.label_bad.setText(_translate("Wizard", "Bad min number points:"))
        self.label_prozent_3.setText(_translate("Wizard", "%"))
        self.label_exercise_name.setText(_translate("Wizard", "Name of the exercise:"))
