import os

import jsonpickle
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QIntValidator
from PyQt5.QtWidgets import QWizard, QFileDialog

from isar.handskilllearning.handskill_exercise_model import FollowThePathExercise
from isar.scene.annotationmodel import CurveAnnotation
from isar.scene.scenemodel import ScenesModel


class HandSkillExercisePathUI(QWizard):

    def __init__(self):
        super().__init__()
        self.exercise = FollowThePathExercise()
        self.scenes_model = ScenesModel()
        self.__scenes = None
        self.setup_ui(self)
        self.setWindowTitle("Follow the path exercise")
        self.setup_signals()
        self.setup_constraints()    

    def setup_signals(self):
        self.button_load_project.clicked.connect(self.button_load_project_clicked)
        self.button_select_scene.clicked.connect(self.button_select_scene_clicked)
        self.button(QWizard.FinishButton).clicked.connect(self.finish_clicked)

        self.line_error_beg.textEdited.connect(self.show_weighted_beginner)
        self.line_time_beg.textEdited.connect(self.show_weighted_beginner)
        self.line_error_weighted_beg.textEdited.connect(self.show_weighted_beginner)
        self.line_time_weighted_beg.textEdited.connect(self.show_weighted_beginner)

        self.line_error_int.textEdited.connect(self.show_weighted_intermediate)
        self.line_time_int.textEdited.connect(self.show_weighted_intermediate)
        self.line_error_weighted_int.textEdited.connect(self.show_weighted_intermediate)
        self.line_time_weighted_int.textEdited.connect(self.show_weighted_intermediate)

        self.line_error_com.textEdited.connect(self.show_weighted_competent)
        self.line_time_com.textEdited.connect(self.show_weighted_competent)
        self.line_error_weighted_com.textEdited.connect(self.show_weighted_competent)
        self.line_time_weighted_com.textEdited.connect(self.show_weighted_competent)

    def button_load_project_clicked(self):
        project_filename = QFileDialog.getOpenFileName(filter="(*.json)")[0]
        project_dir = os.path.dirname(project_filename)
        project_name = os.path.splitext(os.path.basename(project_filename))[0]
        if project_dir is None or project_dir == "":
            return

        self.line_project_name.setText(project_name)
        self.button_select_scene.setEnabled(True)

        # loading prom json file
        global current_project
        model = QStandardItemModel()
        load_path = os.path.join(project_dir, project_name + ".json")
        with open(load_path, "r") as f:
            frozen = f.read()
            current_project = jsonpickle.decode(frozen)
            self.__scenes = current_project.scenes
            for scene in self.__scenes:
                scene.reset_runtime_state()

                # TODO: reimplement. For now just the scenes with one CurveAnnootation are selected
                # select just the scenes which are relevant for this exercise
                if len(scene.get_all_annotations()) == 1 and isinstance(scene.get_all_annotations()[0],
                                                                        CurveAnnotation):
                    item = QStandardItem()
                    item.setText(scene.name)
                    model.appendRow(item)

        self.list_scenes.setModel(model)

    def button_select_scene_clicked(self):
        index = self.list_scenes.currentIndex()
        selected = index.data()
        self.line_selected_scenes.setText(selected)
        for scene in self.__scenes:
            if scene.name == selected:
                self.exercise.set_scene(scene)

    def show_weighted_beginner(self):
        if self.line_error_beg.text() != "" and self.line_time_beg.text() != "" \
                and self.line_error_weighted_beg.text() != "" and self.line_time_weighted_beg.text() != "":
            weighted = self.compute_weighted_combination(int(self.line_error_beg.text()),
                                                         int(self.line_error_weighted_beg.text()),
                                                         int(self.line_time_beg.text()),
                                                         int(self.line_time_weighted_beg.text()))
            self.line_weighted_beg.setText(str(weighted))

    def show_weighted_intermediate(self):
        if self.line_error_int.text() != "" and self.line_time_int.text() != "" \
                and self.line_error_weighted_int.text() != "" and self.line_time_weighted_int.text() != "":
            weighted = self.compute_weighted_combination(int(self.line_error_int.text()),
                                                  int(self.line_error_weighted_int.text()),
                                                  int(self.line_time_int.text()),
                                                  int(self.line_time_weighted_int.text()))
            self.line_weighted_int.setText(str(weighted))

    def show_weighted_competent(self):
        if self.line_error_com.text() != "" and self.line_time_com.text() != "" \
                and self.line_error_weighted_com.text() != "" and self.line_time_weighted_com.text() != "":
            weighted = self.compute_weighted_combination(int(self.line_error_com.text()),
                                                  int(self.line_error_weighted_com.text()),
                                                  int(self.line_time_com.text()),
                                                  int(self.line_time_weighted_com.text()))
            self.line_weighted_com.setText(str(weighted))
    
    def compute_weighted_combination(self, err, const_err, time, const_time):
        return err * const_err + time * const_time

    def finish_clicked(self):
        self.save_info_target_values()
        self.save_info_feedback()
        self.save_exercise()

    def save_info_target_values(self):
        self.exercise.error.beginner.set_value(int(self.line_error_beg.text()))
        self.exercise.error.beginner.set_value_weighted_combination(int(self.line_error_weighted_beg.text()))
        self.exercise.time.beginner.set_value(int(self.line_time_beg.text()))
        self.exercise.time.beginner.set_value_weighted_combination(int(self.line_time_weighted_beg.text()))

        self.exercise.error.intermediate.set_value(int(self.line_error_int.text()))
        self.exercise.error.intermediate.set_value_weighted_combination(int(self.line_error_weighted_int.text()))
        self.exercise.time.intermediate.set_value(int(self.line_time_int.text()))
        self.exercise.time.intermediate.set_value_weighted_combination(int(self.line_time_weighted_int.text()))

        self.exercise.error.competent.set_value(int(self.line_error_com.text()))
        self.exercise.error.competent.set_value_weighted_combination(int(self.line_error_weighted_com.text()))
        self.exercise.time.competent.set_value(int(self.line_time_com.text()))
        self.exercise.time.competent.set_value_weighted_combination(int(self.line_time_weighted_com.text()))

    def save_info_feedback(self):
        if self.radio_button_error.isChecked():
            self.exercise.feedback.value_beginner = self.exercise.error.beginner.get_value()
            self.exercise.feedback.value_intermediate = self.exercise.error.intermediate.get_value()
            self.exercise.feedback.value_competent = self.exercise.error.competent.get_value()

        if self.radio_button_time.isChecked():
            self.exercise.feedback.value_beginner = self.exercise.time.beginner.get_value()
            self.exercise.feedback.value_intermediate = self.exercise.time.intermediate.get_value()
            self.exercise.feedback.value_competent = self.exercise.time.competent.get_value()

        if self.radio_button_weighted.isChecked():
            self.exercise.feedback.value_beginner = \
                self.compute_weighted_combination(int(self.line_error_beg.text()),
                                                  int(self.line_error_weighted_beg.text()),
                                                  int(self.line_time_beg.text()),
                                                  int(self.line_time_weighted_beg.text()))

            self.exercise.feedback.value_intermediate = \
                self.compute_weighted_combination(int(self.line_error_int.text()),
                                                  int(self.line_error_weighted_int.text()),
                                                  int(self.line_time_int.text()),
                                                  int(self.line_time_weighted_int.text()))

            self.exercise.feedback.value_competent = \
                self.compute_weighted_combination(int(self.line_error_com.text()),
                                                  int(self.line_error_weighted_com.text()),
                                                  int(self.line_time_com.text()),
                                                  int(self.line_time_weighted_com.text()))

        self.exercise.feedback.set_good((int(self.line_good_from.text()), int(self.line_good_to.text())))
        self.exercise.feedback.set_average((int(self.line_average_from.text()), int(self.line_average_to.text())))
        self.exercise.feedback.set_bad((int(self.line_bad_from.text()), int(self.line_bad_to.text())))

    def save_exercise(self):
        parent_dir = QFileDialog.getExistingDirectory()
        if parent_dir is None or parent_dir == "":
            return

        project_name = self.line_exercise_name.text()

        save_path = os.path.join(parent_dir, project_name + ".json")

        frozen = jsonpickle.encode(self.exercise)
        with open(str(save_path), "w") as f:
            f.write(frozen)

    def setup_constraints(self):
        # register fields to enable/disable the next/finish button
        self.scene.registerField("line_selected_scenes*", self.line_selected_scenes)
        self.target_value.registerField("line_error_beg*", self.line_error_beg)
        self.target_value.registerField("line_time_beg*", self.line_time_beg)
        self.target_value.registerField("line_error_weighted_beg*", self.line_error_weighted_beg)
        self.target_value.registerField("line_time_weighted_beg*", self.line_time_weighted_beg)
        self.target_value.registerField("line_error_int*", self.line_error_int)
        self.target_value.registerField("line_time_int*", self.line_time_int)
        self.target_value.registerField("line_error_weighted_int*", self.line_error_weighted_int)
        self.target_value.registerField("line_time_weighted_int*", self.line_time_weighted_int)
        self.target_value.registerField("line_error_com*", self.line_error_com)
        self.target_value.registerField("line_time_com*", self.line_time_com)
        self.target_value.registerField("line_error_weighted_com*", self.line_error_weighted_com)
        self.target_value.registerField("line_time_weighted_com*", self.line_time_weighted_com)
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
        self.line_error_weighted_beg.setValidator(QIntValidator())
        self.line_time_weighted_beg.setValidator(QIntValidator())
        self.line_error_int.setValidator(QIntValidator())
        self.line_time_int.setValidator(QIntValidator())
        self.line_error_weighted_int.setValidator(QIntValidator())
        self.line_time_weighted_int.setValidator(QIntValidator())
        self.line_error_com.setValidator(QIntValidator())
        self.line_time_com.setValidator(QIntValidator())
        self.line_error_weighted_com.setValidator(QIntValidator())
        self.line_time_weighted_com.setValidator(QIntValidator())
        self.line_good_from.setValidator(QIntValidator())
        self.line_good_to.setValidator(QIntValidator())
        self.line_average_from.setValidator(QIntValidator())
        self.line_average_to.setValidator(QIntValidator())
        self.line_bad_from.setValidator(QIntValidator())
        self.line_bad_to.setValidator(QIntValidator())

        self.line_project_name.setEnabled(False)
        self.line_selected_scenes.setEnabled(False)
        self.button_select_scene.setEnabled(False)
        self.line_weighted_beg.setEnabled(False)
        self.line_weighted_int.setEnabled(False)
        self.line_weighted_com.setEnabled(False)
        self.radio_button_error.setChecked(True)

    def setup_ui(self, Wizard):
        Wizard.setObjectName("Wizard")
        Wizard.resize(500, 500)
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
        self.line_selected_scenes = QtWidgets.QLineEdit(self.scene)
        self.line_selected_scenes.setObjectName("line_selected_scenes")
        self.gridLayout.addWidget(self.line_selected_scenes, 4, 2, 1, 2)
        self.button_select_scene = QtWidgets.QPushButton(self.scene)
        self.button_select_scene.setObjectName("button_select_scene")
        self.gridLayout.addWidget(self.button_select_scene, 3, 3, 1, 1)
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
        self.label_weighted = QtWidgets.QLabel(self.target_value)
        self.label_weighted.setObjectName("label_weighted")
        self.gridLayout_2.addWidget(self.label_weighted, 2, 0, 1, 3)
        self.label_error_weighted = QtWidgets.QLabel(self.target_value)
        self.label_error_weighted.setObjectName("label_error_weighted")
        self.gridLayout_2.addWidget(self.label_error_weighted, 3, 0, 1, 1)
        self.line_error_weighted_beg = QtWidgets.QLineEdit(self.target_value)
        self.line_error_weighted_beg.setObjectName("line_error_weighted_beg")
        self.gridLayout_2.addWidget(self.line_error_weighted_beg, 3, 1, 1, 1)
        self.label_time_weighted = QtWidgets.QLabel(self.target_value)
        self.label_time_weighted.setObjectName("label_time_weighted")
        self.gridLayout_2.addWidget(self.label_time_weighted, 3, 2, 1, 1)
        self.line_time_weighted_beg = QtWidgets.QLineEdit(self.target_value)
        self.line_time_weighted_beg.setObjectName("line_time_weighted_beg")
        self.gridLayout_2.addWidget(self.line_time_weighted_beg, 3, 3, 1, 1)
        self.line_weighted_beg = QtWidgets.QLineEdit(self.target_value)
        self.line_weighted_beg.setObjectName("line_weighted_beg")
        self.gridLayout_2.addWidget(self.line_weighted_beg, 3, 4, 1, 1)
        self.label_skill_level_2 = QtWidgets.QLabel(self.target_value)
        self.label_skill_level_2.setObjectName("label_skill_level_2")
        self.gridLayout_2.addWidget(self.label_skill_level_2, 4, 0, 1, 2)
        self.label_error_2 = QtWidgets.QLabel(self.target_value)
        self.label_error_2.setObjectName("label_error_2")
        self.gridLayout_2.addWidget(self.label_error_2, 5, 0, 1, 1)
        self.line_error_int = QtWidgets.QLineEdit(self.target_value)
        self.line_error_int.setObjectName("line_error_int")
        self.gridLayout_2.addWidget(self.line_error_int, 5, 1, 1, 1)
        self.label_time_2 = QtWidgets.QLabel(self.target_value)
        self.label_time_2.setObjectName("label_time_2")
        self.gridLayout_2.addWidget(self.label_time_2, 5, 2, 1, 1)
        self.label_weighted_2 = QtWidgets.QLabel(self.target_value)
        self.label_weighted_2.setObjectName("label_weighted_2")
        self.gridLayout_2.addWidget(self.label_weighted_2, 6, 0, 1, 3)
        self.label_error_weighted_2 = QtWidgets.QLabel(self.target_value)
        self.label_error_weighted_2.setObjectName("label_error_weighted_2")
        self.gridLayout_2.addWidget(self.label_error_weighted_2, 7, 0, 1, 1)
        self.line_error_weighted_int = QtWidgets.QLineEdit(self.target_value)
        self.line_error_weighted_int.setObjectName("line_error_weighted_int")
        self.gridLayout_2.addWidget(self.line_error_weighted_int, 7, 1, 1, 1)
        self.label_time_weighted_2 = QtWidgets.QLabel(self.target_value)
        self.label_time_weighted_2.setObjectName("label_time_weighted_2")
        self.gridLayout_2.addWidget(self.label_time_weighted_2, 7, 2, 1, 1)
        self.line_time_weighted_int = QtWidgets.QLineEdit(self.target_value)
        self.line_time_weighted_int.setObjectName("line_time_weighted_int")
        self.gridLayout_2.addWidget(self.line_time_weighted_int, 7, 3, 1, 1)
        self.line_weighted_int = QtWidgets.QLineEdit(self.target_value)
        self.line_weighted_int.setObjectName("line_weighted_int")
        self.gridLayout_2.addWidget(self.line_weighted_int, 7, 4, 1, 1)
        self.label_skill_level_3 = QtWidgets.QLabel(self.target_value)
        self.label_skill_level_3.setObjectName("label_skill_level_3")
        self.gridLayout_2.addWidget(self.label_skill_level_3, 8, 0, 1, 2)
        self.label_error_3 = QtWidgets.QLabel(self.target_value)
        self.label_error_3.setObjectName("label_error_3")
        self.gridLayout_2.addWidget(self.label_error_3, 9, 0, 1, 1)
        self.line_error_com = QtWidgets.QLineEdit(self.target_value)
        self.line_error_com.setObjectName("line_error_com")
        self.gridLayout_2.addWidget(self.line_error_com, 9, 1, 1, 1)
        self.label_time_3 = QtWidgets.QLabel(self.target_value)
        self.label_time_3.setObjectName("label_time_3")
        self.gridLayout_2.addWidget(self.label_time_3, 9, 2, 1, 1)
        self.label_weighted_3 = QtWidgets.QLabel(self.target_value)
        self.label_weighted_3.setObjectName("label_weighted_3")
        self.gridLayout_2.addWidget(self.label_weighted_3, 10, 0, 1, 3)
        self.label_error_weighted_3 = QtWidgets.QLabel(self.target_value)
        self.label_error_weighted_3.setObjectName("label_error_weighted_3")
        self.gridLayout_2.addWidget(self.label_error_weighted_3, 11, 0, 1, 1)
        self.line_error_weighted_com = QtWidgets.QLineEdit(self.target_value)
        self.line_error_weighted_com.setObjectName("line_error_weighted_com")
        self.gridLayout_2.addWidget(self.line_error_weighted_com, 11, 1, 1, 1)
        self.label_time_weighted_3 = QtWidgets.QLabel(self.target_value)
        self.label_time_weighted_3.setObjectName("label_time_weighted_3")
        self.gridLayout_2.addWidget(self.label_time_weighted_3, 11, 2, 1, 1)
        self.line_time_weighted_com = QtWidgets.QLineEdit(self.target_value)
        self.line_time_weighted_com.setObjectName("line_time_weighted_com")
        self.gridLayout_2.addWidget(self.line_time_weighted_com, 11, 3, 1, 1)
        self.line_weighted_com = QtWidgets.QLineEdit(self.target_value)
        self.line_weighted_com.setObjectName("line_weighted_com")
        self.gridLayout_2.addWidget(self.line_weighted_com, 11, 4, 1, 1)
        self.line_time_int = QtWidgets.QLineEdit(self.target_value)
        self.line_time_int.setObjectName("line_time_int")
        self.gridLayout_2.addWidget(self.line_time_int, 4, 3, 3, 1)
        self.line_time_com = QtWidgets.QLineEdit(self.target_value)
        self.line_time_com.setObjectName("line_time_com")
        self.gridLayout_2.addWidget(self.line_time_com, 8, 3, 3, 1)
        self.line_time_beg = QtWidgets.QLineEdit(self.target_value)
        self.line_time_beg.setObjectName("line_time_beg")
        self.gridLayout_2.addWidget(self.line_time_beg, 0, 3, 3, 1)
        Wizard.addPage(self.target_value)

        self.feedback = QtWidgets.QWizardPage()
        self.feedback.setObjectName("feedback")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.feedback)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.label_aspect = QtWidgets.QLabel(self.feedback)
        self.label_aspect.setObjectName("label_aspect")
        self.gridLayout_3.addWidget(self.label_aspect, 0, 0, 1, 5)
        self.radio_button_error = QtWidgets.QRadioButton(self.feedback)
        self.radio_button_error.setObjectName("radio_button_error")
        self.gridLayout_3.addWidget(self.radio_button_error, 1, 0, 1, 2)
        self.radio_button_time = QtWidgets.QRadioButton(self.feedback)
        self.radio_button_time.setObjectName("radio_button_time")
        self.gridLayout_3.addWidget(self.radio_button_time, 2, 0, 1, 2)
        self.radio_button_weighted = QtWidgets.QRadioButton(self.feedback)
        self.radio_button_weighted.setObjectName("radio_button_weighted")
        self.gridLayout_3.addWidget(self.radio_button_weighted, 3, 0, 1, 3)
        self.label_good = QtWidgets.QLabel(self.feedback)
        self.label_good.setObjectName("label_good")
        self.gridLayout_3.addWidget(self.label_good, 4, 0, 1, 1)
        self.label_from_1 = QtWidgets.QLabel(self.feedback)
        self.label_from_1.setObjectName("label_from_1")
        self.gridLayout_3.addWidget(self.label_from_1, 4, 1, 1, 1)
        self.line_good_from = QtWidgets.QLineEdit(self.feedback)
        self.line_good_from.setObjectName("line_good_from")
        self.gridLayout_3.addWidget(self.line_good_from, 4, 2, 1, 1)
        self.label_to_1 = QtWidgets.QLabel(self.feedback)
        self.label_to_1.setObjectName("label_to_1")
        self.gridLayout_3.addWidget(self.label_to_1, 4, 3, 1, 1)
        self.line_good_to = QtWidgets.QLineEdit(self.feedback)
        self.line_good_to.setObjectName("line_good_to")
        self.gridLayout_3.addWidget(self.line_good_to, 4, 4, 1, 1)
        self.label_average = QtWidgets.QLabel(self.feedback)
        self.label_average.setObjectName("label_average")
        self.gridLayout_3.addWidget(self.label_average, 5, 0, 1, 1)
        self.label_from_2 = QtWidgets.QLabel(self.feedback)
        self.label_from_2.setObjectName("label_from_2")
        self.gridLayout_3.addWidget(self.label_from_2, 5, 1, 1, 1)
        self.line_average_from = QtWidgets.QLineEdit(self.feedback)
        self.line_average_from.setObjectName("line_average_from")
        self.gridLayout_3.addWidget(self.line_average_from, 5, 2, 1, 1)
        self.label_to_2 = QtWidgets.QLabel(self.feedback)
        self.label_to_2.setObjectName("label_to_2")
        self.gridLayout_3.addWidget(self.label_to_2, 5, 3, 1, 1)
        self.line_average_to = QtWidgets.QLineEdit(self.feedback)
        self.line_average_to.setObjectName("line_average_to")
        self.gridLayout_3.addWidget(self.line_average_to, 5, 4, 1, 1)
        self.label_bad = QtWidgets.QLabel(self.feedback)
        self.label_bad.setObjectName("label_bad")
        self.gridLayout_3.addWidget(self.label_bad, 6, 0, 1, 1)
        self.label_from_3 = QtWidgets.QLabel(self.feedback)
        self.label_from_3.setObjectName("label_from_3")
        self.gridLayout_3.addWidget(self.label_from_3, 6, 1, 1, 1)
        self.line_bad_from = QtWidgets.QLineEdit(self.feedback)
        self.line_bad_from.setObjectName("line_bad_from")
        self.gridLayout_3.addWidget(self.line_bad_from, 6, 2, 1, 1)
        self.label_to_3 = QtWidgets.QLabel(self.feedback)
        self.label_to_3.setObjectName("label_to_3")
        self.gridLayout_3.addWidget(self.label_to_3, 6, 3, 1, 1)
        self.line_bad_to = QtWidgets.QLineEdit(self.feedback)
        self.line_bad_to.setObjectName("line_bad_to")
        self.gridLayout_3.addWidget(self.line_bad_to, 6, 4, 1, 1)
        self.label_exercise_name = QtWidgets.QLabel(self.feedback)
        self.label_exercise_name.setObjectName("label_exercise_name")
        self.gridLayout_3.addWidget(self.label_exercise_name, 7, 0, 1, 3)
        self.line_exercise_name = QtWidgets.QLineEdit(self.feedback)
        self.line_exercise_name.setObjectName("line_exercise_name")
        self.gridLayout_3.addWidget(self.line_exercise_name, 8, 0, 1, 3)
        Wizard.addPage(self.feedback)

        self.retranslate_ui(Wizard)
        QtCore.QMetaObject.connectSlotsByName(Wizard)
        Wizard.setTabOrder(self.button_load_project, self.line_project_name)
        Wizard.setTabOrder(self.line_project_name, self.list_scenes)
        Wizard.setTabOrder(self.list_scenes, self.button_select_scene)
        Wizard.setTabOrder(self.button_select_scene, self.line_selected_scenes)
        Wizard.setTabOrder(self.line_selected_scenes, self.line_error_beg)
        Wizard.setTabOrder(self.line_error_beg, self.line_time_beg)
        Wizard.setTabOrder(self.line_time_beg, self.line_error_weighted_beg)
        Wizard.setTabOrder(self.line_error_weighted_beg, self.line_time_weighted_beg)
        Wizard.setTabOrder(self.line_time_weighted_beg, self.line_error_int)
        Wizard.setTabOrder(self.line_error_int, self.line_time_int)
        Wizard.setTabOrder(self.line_time_int, self.line_error_weighted_int)
        Wizard.setTabOrder(self.line_error_weighted_int, self.line_time_weighted_int)
        Wizard.setTabOrder(self.line_time_weighted_int, self.line_error_com)
        Wizard.setTabOrder(self.line_error_com, self.line_time_com)
        Wizard.setTabOrder(self.line_time_com, self.line_error_weighted_com)
        Wizard.setTabOrder(self.line_error_weighted_com, self.line_time_weighted_com)
        Wizard.setTabOrder(self.line_time_weighted_com, self.line_weighted_beg)
        Wizard.setTabOrder(self.line_weighted_beg, self.line_weighted_int)
        Wizard.setTabOrder(self.line_weighted_int, self.line_weighted_com)
        Wizard.setTabOrder(self.line_weighted_com, self.radio_button_error)
        Wizard.setTabOrder(self.radio_button_error, self.radio_button_time)
        Wizard.setTabOrder(self.radio_button_time, self.radio_button_weighted)
        Wizard.setTabOrder(self.radio_button_weighted, self.line_good_from)
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
        self.button_select_scene.setText(_translate("Wizard", "Select"))
        self.label_selected.setText(_translate("Wizard", "Selected scene:"))
        self.label_project_name.setText(_translate("Wizard", "Project name:"))
        self.label_scenes.setText(_translate("Wizard", "Scenes:"))
        self.label_skill_level.setText(_translate("Wizard", "Skill level beginner:"))
        self.label_error.setText(_translate("Wizard", "Error:"))
        self.label_time.setText(_translate("Wizard", "Time:"))
        self.label_weighted.setText(_translate("Wizard", "Weighted combination:"))
        self.label_error_weighted.setText(_translate("Wizard", "Error:"))
        self.label_time_weighted.setText(_translate("Wizard", "Time:"))
        self.label_skill_level_2.setText(_translate("Wizard", "Skill level intermediate:"))
        self.label_error_2.setText(_translate("Wizard", "Error:"))
        self.label_time_2.setText(_translate("Wizard", "Time:"))
        self.label_weighted_2.setText(_translate("Wizard", "Weighted combination:"))
        self.label_error_weighted_2.setText(_translate("Wizard", "Error:"))
        self.label_time_weighted_2.setText(_translate("Wizard", "Time:"))
        self.label_skill_level_3.setText(_translate("Wizard", "Skill level competent:"))
        self.label_error_3.setText(_translate("Wizard", "Error:"))
        self.label_time_3.setText(_translate("Wizard", "Time:"))
        self.label_weighted_3.setText(_translate("Wizard", "Weighted combination:"))
        self.label_error_weighted_3.setText(_translate("Wizard", "Error:"))
        self.label_time_weighted_3.setText(_translate("Wizard", "Time:"))
        self.label_aspect.setText(_translate("Wizard", "Aspect for the given the feedback:"))
        self.radio_button_error.setText(_translate("Wizard", "Error"))
        self.radio_button_time.setText(_translate("Wizard", "Time"))
        self.radio_button_weighted.setText(_translate("Wizard", "Weighted combination"))
        self.label_good.setText(_translate("Wizard", "Good:"))
        self.label_from_1.setText(_translate("Wizard", "from"))
        self.label_to_1.setText(_translate("Wizard", "to"))
        self.label_average.setText(_translate("Wizard", "Average:"))
        self.label_from_2.setText(_translate("Wizard", "from"))
        self.label_to_2.setText(_translate("Wizard", "to"))
        self.label_bad.setText(_translate("Wizard", "Bad:"))
        self.label_from_3.setText(_translate("Wizard", "from"))
        self.label_to_3.setText(_translate("Wizard", "to"))
        self.label_exercise_name.setText(_translate("Wizard", "Name of the exercise:"))