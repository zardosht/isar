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
        if self.radio_button_error.isChecked():
            self.exercise.feedback.value_beginner = self.exercise.error.beginner.get_value()
            self.exercise.feedback.value_intermediate = self.exercise.error.intermediate.get_value()
            self.exercise.feedback.value_competent = self.exercise.error.competent.get_value()

        if self.radio_button_time.isChecked():
            self.exercise.feedback.value_beginner = self.exercise.time.beginner.get_value()
            self.exercise.feedback.value_intermediate = self.exercise.time.intermediate.get_value()
            self.exercise.feedback.value_competent = self.exercise.time.competent.get_value()

        self.exercise.feedback.set_good((int(self.line_good_from.text()), int(self.line_good_to.text())))
        self.exercise.feedback.set_average((int(self.line_average_from.text()), int(self.line_average_to.text())))
        self.exercise.feedback.set_bad((int(self.line_bad_from.text()), int(self.line_bad_to.text())))

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

    def setup_constraints(self):
        # register fields to enable/disable the next/finish button
        self.scene.registerField("line_selected_scenes*", self.line_selected_scenes)
        self.target_value.registerField("line_error_beg*", self.line_error_beg)
        self.target_value.registerField("line_time_beg*", self.line_time_beg)
        self.target_value.registerField("line_error_int*", self.line_error_int)
        self.target_value.registerField("line_time_int*", self.line_time_int)
        self.target_value.registerField("line_error_com*", self.line_error_com)
        self.target_value.registerField("line_time_com*", self.line_time_com)
        self.feedback.registerField("line_good_to*", self.line_good_to)
        self.feedback.registerField("line_good_from*", self.line_good_from)
        self.feedback.registerField("line_average_to*", self.line_average_to)
        self.feedback.registerField("line_average_from*", self.line_average_from)
        self.feedback.registerField("line_bad_to*", self.line_bad_to)
        self.feedback.registerField("line_bad_from*", self.line_bad_from)
        self.feedback.registerField("line_exercise_name*", self.line_exercise_name)

        # set the line edit content to be a number
        self.line_error_beg.setValidator(QIntValidator())
        self.line_time_beg.setValidator(QIntValidator())
        self.line_error_int.setValidator(QIntValidator())
        self.line_time_int.setValidator(QIntValidator())
        self.line_error_com.setValidator(QIntValidator())
        self.line_time_com.setValidator(QIntValidator())
        self.line_good_from.setValidator(QIntValidator())
        self.line_good_to.setValidator(QIntValidator())
        self.line_average_from.setValidator(QIntValidator())
        self.line_average_to.setValidator(QIntValidator())
        self.line_bad_from.setValidator(QIntValidator())
        self.line_bad_to.setValidator(QIntValidator())

        self.line_project_name.setEnabled(False)
        self.line_selected_scenes.setEnabled(False)
        self.button_select_scene.setEnabled(False)
        self.radio_button_error.setChecked(True)

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
        self.label_skill_level = QtWidgets.QLabel(self.target_value)
        self.label_skill_level.setObjectName("label_skill_level")
        self.gridLayout_2.addWidget(self.label_skill_level, 0, 0, 1, 2)
        self.label_error = QtWidgets.QLabel(self.target_value)
        self.label_error.setObjectName("label_error")
        self.gridLayout_2.addWidget(self.label_error, 1, 0, 1, 1)
        self.line_error_beg = QtWidgets.QLineEdit(self.target_value)
        self.line_error_beg.setObjectName("line_error_beg")
        self.gridLayout_2.addWidget(self.line_error_beg, 1, 1, 1, 1)
        self.label_time = QtWidgets.QLabel(self.target_value)
        self.label_time.setObjectName("label_time")
        self.gridLayout_2.addWidget(self.label_time, 1, 2, 1, 1)
        self.line_time_beg = QtWidgets.QLineEdit(self.target_value)
        self.line_time_beg.setObjectName("line_time_beg")
        self.gridLayout_2.addWidget(self.line_time_beg, 1, 3, 1, 1)
        self.label_skill_level_2 = QtWidgets.QLabel(self.target_value)
        self.label_skill_level_2.setObjectName("label_skill_level_2")
        self.gridLayout_2.addWidget(self.label_skill_level_2, 2, 0, 1, 2)
        self.label_error_2 = QtWidgets.QLabel(self.target_value)
        self.label_error_2.setObjectName("label_error_2")
        self.gridLayout_2.addWidget(self.label_error_2, 3, 0, 1, 1)
        self.line_error_int = QtWidgets.QLineEdit(self.target_value)
        self.line_error_int.setObjectName("line_error_int")
        self.gridLayout_2.addWidget(self.line_error_int, 3, 1, 1, 1)
        self.label_time_2 = QtWidgets.QLabel(self.target_value)
        self.label_time_2.setObjectName("label_time_2")
        self.gridLayout_2.addWidget(self.label_time_2, 3, 2, 1, 1)
        self.line_time_int = QtWidgets.QLineEdit(self.target_value)
        self.line_time_int.setObjectName("line_time_int")
        self.gridLayout_2.addWidget(self.line_time_int, 3, 3, 1, 1)
        self.label_skill_level_3 = QtWidgets.QLabel(self.target_value)
        self.label_skill_level_3.setObjectName("label_skill_level_3")
        self.gridLayout_2.addWidget(self.label_skill_level_3, 4, 0, 1, 2)
        self.label_error_3 = QtWidgets.QLabel(self.target_value)
        self.label_error_3.setObjectName("label_error_3")
        self.gridLayout_2.addWidget(self.label_error_3, 5, 0, 1, 1)
        self.line_error_com = QtWidgets.QLineEdit(self.target_value)
        self.line_error_com.setObjectName("line_error_com")
        self.gridLayout_2.addWidget(self.line_error_com, 5, 1, 1, 1)
        self.label_time_3 = QtWidgets.QLabel(self.target_value)
        self.label_time_3.setObjectName("label_time_3")
        self.gridLayout_2.addWidget(self.label_time_3, 5, 2, 1, 1)
        self.line_time_com = QtWidgets.QLineEdit(self.target_value)
        self.line_time_com.setObjectName("line_time_com")
        self.gridLayout_2.addWidget(self.line_time_com, 5, 3, 1, 1)
        Wizard.addPage(self.target_value)

        self.feedback = QtWidgets.QWizardPage()
        self.feedback.setObjectName("feedback")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.feedback)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.radio_button_error = QtWidgets.QRadioButton(self.feedback)
        self.radio_button_error.setObjectName("radio_button_error")
        self.gridLayout_3.addWidget(self.radio_button_error, 1, 0, 1, 2)
        self.label_average = QtWidgets.QLabel(self.feedback)
        self.label_average.setObjectName("label_average")
        self.gridLayout_3.addWidget(self.label_average, 4, 0, 1, 1)
        self.label_bad = QtWidgets.QLabel(self.feedback)
        self.label_bad.setObjectName("label_bad")
        self.gridLayout_3.addWidget(self.label_bad, 5, 0, 1, 1)
        self.line_average_to = QtWidgets.QLineEdit(self.feedback)
        self.line_average_to.setObjectName("line_average_to")
        self.gridLayout_3.addWidget(self.line_average_to, 4, 4, 1, 1)
        self.label_to_2 = QtWidgets.QLabel(self.feedback)
        self.label_to_2.setObjectName("label_to_2")
        self.gridLayout_3.addWidget(self.label_to_2, 4, 3, 1, 1)
        self.label_good = QtWidgets.QLabel(self.feedback)
        self.label_good.setObjectName("label_good")
        self.gridLayout_3.addWidget(self.label_good, 3, 0, 1, 1)
        self.line_good_to = QtWidgets.QLineEdit(self.feedback)
        self.line_good_to.setObjectName("line_good_to")
        self.gridLayout_3.addWidget(self.line_good_to, 3, 4, 1, 1)
        self.label_from_3 = QtWidgets.QLabel(self.feedback)
        self.label_from_3.setObjectName("label_from_3")
        self.gridLayout_3.addWidget(self.label_from_3, 5, 1, 1, 1)
        self.line_good_from = QtWidgets.QLineEdit(self.feedback)
        self.line_good_from.setObjectName("line_good_from")
        self.gridLayout_3.addWidget(self.line_good_from, 3, 2, 1, 1)
        self.label_to_3 = QtWidgets.QLabel(self.feedback)
        self.label_to_3.setObjectName("label_to_3")
        self.gridLayout_3.addWidget(self.label_to_3, 5, 3, 1, 1)
        self.label_aspect = QtWidgets.QLabel(self.feedback)
        self.label_aspect.setObjectName("label_aspect")
        self.gridLayout_3.addWidget(self.label_aspect, 0, 0, 1, 5)
        self.label_from_1 = QtWidgets.QLabel(self.feedback)
        self.label_from_1.setObjectName("label_from_1")
        self.gridLayout_3.addWidget(self.label_from_1, 3, 1, 1, 1)
        self.label_to_1 = QtWidgets.QLabel(self.feedback)
        self.label_to_1.setObjectName("label_to_1")
        self.gridLayout_3.addWidget(self.label_to_1, 3, 3, 1, 1)
        self.label_exercise_name = QtWidgets.QLabel(self.feedback)
        self.label_exercise_name.setObjectName("label_exercise_name")
        self.gridLayout_3.addWidget(self.label_exercise_name, 6, 0, 1, 3)
        self.line_exercise_name = QtWidgets.QLineEdit(self.feedback)
        self.line_exercise_name.setObjectName("line_exercise_name")
        self.gridLayout_3.addWidget(self.line_exercise_name, 7, 0, 1, 3)
        self.line_bad_to = QtWidgets.QLineEdit(self.feedback)
        self.line_bad_to.setObjectName("line_bad_to")
        self.gridLayout_3.addWidget(self.line_bad_to, 5, 4, 1, 1)
        self.line_average_from = QtWidgets.QLineEdit(self.feedback)
        self.line_average_from.setObjectName("line_average_from")
        self.gridLayout_3.addWidget(self.line_average_from, 4, 2, 1, 1)
        self.line_bad_from = QtWidgets.QLineEdit(self.feedback)
        self.line_bad_from.setObjectName("line_bad_from")
        self.gridLayout_3.addWidget(self.line_bad_from, 5, 2, 1, 1)
        self.label_from_2 = QtWidgets.QLabel(self.feedback)
        self.label_from_2.setObjectName("label_from_2")
        self.gridLayout_3.addWidget(self.label_from_2, 4, 1, 1, 1)
        self.radio_button_time = QtWidgets.QRadioButton(self.feedback)
        self.radio_button_time.setObjectName("radio_button_time")
        self.gridLayout_3.addWidget(self.radio_button_time, 1, 2, 1, 1)
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
        Wizard.setTabOrder(self.line_time_com, self.radio_button_error)
        Wizard.setTabOrder(self.radio_button_error, self.line_good_from)
        Wizard.setTabOrder(self.line_good_from, self.line_good_to)
        Wizard.setTabOrder(self.line_good_to, self.line_average_from)
        Wizard.setTabOrder(self.line_average_from, self.line_average_to)
        Wizard.setTabOrder(self.line_average_to, self.line_bad_from)
        Wizard.setTabOrder(self.line_bad_from, self.line_bad_to)
        Wizard.setTabOrder(self.line_bad_to, self.line_exercise_name)

    def retranslate_ui(self, Wizard):
        _translate = QtCore.QCoreApplication.translate
        Wizard.setWindowTitle(_translate("Wizard", "Wizard"))
        self.button_load_project.setText(_translate("Wizard", "Load project"))
        self.label_selected.setText(_translate("Wizard", "Selected scene:"))
        self.label_project_name.setText(_translate("Wizard", "Project name:"))
        self.label_scenes.setText(_translate("Wizard", "Scenes:"))
        self.button_select_scene.setText(_translate("Wizard", "Select"))
        self.label_skill_level.setText(_translate("Wizard", "Skill level beginner:"))
        self.label_error.setText(_translate("Wizard", "Error:"))
        self.label_time.setText(_translate("Wizard", "Time:"))
        self.label_skill_level_2.setText(_translate("Wizard", "Skill level intermediate:"))
        self.label_error_2.setText(_translate("Wizard", "Error:"))
        self.label_time_2.setText(_translate("Wizard", "Time:"))
        self.label_skill_level_3.setText(_translate("Wizard", "Skill level competent:"))
        self.label_error_3.setText(_translate("Wizard", "Error:"))
        self.label_time_3.setText(_translate("Wizard", "Time:"))
        self.radio_button_error.setText(_translate("Wizard", "Error"))
        self.label_average.setText(_translate("Wizard", "Average:"))
        self.label_bad.setText(_translate("Wizard", "Bad:"))
        self.label_to_2.setText(_translate("Wizard", "to"))
        self.label_good.setText(_translate("Wizard", "Good:"))
        self.label_from_3.setText(_translate("Wizard", "from"))
        self.label_to_3.setText(_translate("Wizard", "to"))
        self.label_aspect.setText(_translate("Wizard", "Aspect for the given the feedback:"))
        self.label_from_1.setText(_translate("Wizard", "from"))
        self.label_to_1.setText(_translate("Wizard", "to"))
        self.label_exercise_name.setText(_translate("Wizard", "Name of the exercise:"))
        self.label_from_2.setText(_translate("Wizard", "from"))
        self.radio_button_time.setText(_translate("Wizard", "Time"))
