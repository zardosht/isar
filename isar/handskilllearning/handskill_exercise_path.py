import os

import jsonpickle
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QWizard, QFileDialog

from isar.handskilllearning.handskill_exercise_model import FollowThePathExercise, Beginner
from isar.scene.annotationmodel import CurveAnnotation
from isar.scene.scenemodel import ScenesModel


class HandSkillExercisePathUI(QWizard):

    def __init__(self):
        super().__init__()
        self.exercise = FollowThePathExercise()
        self.scenes_model = ScenesModel()
        self.__scenes = None
        self.setup_ui(self)
        self.setup_signals()
        self.setup_constraints()

        # TODO: set title and set style
        self.setButtonText(QWizard.FinishButton, "&Save and Finish");

    def setup_signals(self):
        self.pushButton_loadProject.clicked.connect(self.pushButton_loadProject_clicked)
        self.pushButton_selectScene.clicked.connect(self.pushButton_selectScene_clicked)
        self.button(QWizard.FinishButton).clicked.connect(self.finish_clicked)

    def finish_clicked(self):
        self.save_info_target_values()
        self.save_info_feedback()
        self.save_exercise()
        print("Finish!")

    def save_info_target_values(self):
        self.exercise.error.beginner.set_value(int(self.lineEdit_error_beg.text()))
        self.exercise.error.beginner.set_value_weighted_combination(int(self.lineEdit_errorWeighted_beg.text()))
        self.exercise.time.beginner.set_value(int(self.lineEdit_time_beg.text()))
        self.exercise.time.beginner.set_value_weighted_combination(int(self.lineEdit_timeWeighted_beg.text()))

        self.exercise.error.intermediate.set_value(int(self.lineEdit_error_int.text()))
        self.exercise.error.intermediate.set_value_weighted_combination(int(self.lineEdit_errorWeighted_int.text()))
        self.exercise.time.intermediate.set_value(int(self.lineEdit_time_int.text()))
        self.exercise.time.intermediate.set_value_weighted_combination(int(self.lineEdit_timeWeighted_int.text()))

        self.exercise.error.competent.set_value(int(self.lineEdit_error_com.text()))
        self.exercise.error.competent.set_value_weighted_combination(int(self.lineEdit_errorWeighted_com.text()))
        self.exercise.time.competent.set_value(int(self.lineEdit_time_com.text()))
        self.exercise.time.competent.set_value_weighted_combination(int(self.lineEdit_timeWeighted_com.text()))


    def compute_weighted_combination(self, err, const_err, time, const_time):
        return err * const_err + time * const_time

    def save_info_feedback(self):
        if self.radioButton_error.isChecked():
            self.exercise.feedback.value_beginner = self.exercise.error.beginner.get_value()
            self.exercise.feedback.value_intermediate = self.exercise.error.intermediate.get_value()
            self.exercise.feedback.value_competent = self.exercise.error.competent.get_value()

        if self.radioButton_time.isChecked():
            self.exercise.feedback.value_beginner = self.exercise.time.beginner.get_value()
            self.exercise.feedback.value_intermediate = self.exercise.time.intermediate.get_value()
            self.exercise.feedback.value_competent = self.exercise.time.competent.get_value()

        if self.radioButton_weighted.isChecked():
            self.exercise.feedback.value_beginner = \
                self.compute_weighted_combination(int(self.lineEdit_error_beg.text()),
                                                  int(self.lineEdit_errorWeighted_beg.text()),
                                                  int(self.lineEdit_time_beg.text()),
                                                  int(self.lineEdit_timeWeighted_beg.text()))

            self.exercise.feedback.value_intermediate = \
                self.compute_weighted_combination(int(self.lineEdit_error_int.text()),
                                                  int(self.lineEdit_errorWeighted_int.text()),
                                                  int(self.lineEdit_time_int.text()),
                                                  int(self.lineEdit_timeWeighted_int.text()))

            self.exercise.feedback.value_competent = \
                self.compute_weighted_combination(int(self.lineEdit_error_com.text()),
                                                  int(self.lineEdit_errorWeighted_com.text()),
                                                  int(self.lineEdit_time_com.text()),
                                                  int(self.lineEdit_timeWeighted_com.text()))

        self.exercise.feedback.set_good((int(self.lineEdit_goodFrom.text()), int(self.lineEdit_goodTo.text())))
        self.exercise.feedback.set_average((int(self.lineEdit_averageFrom.text()), int(self.lineEdit_averageTo.text())))
        self.exercise.feedback.set_bad((int(self.lineEdit_badFrom.text()), int(self.lineEdit_badTo.text())))

    def save_exercise(self):
        parent_dir = QFileDialog.getExistingDirectory()
        if parent_dir is None or parent_dir == "":
            return

        project_name = self.lineEdit_exerciseName.text()

        save_path = os.path.join(parent_dir, project_name + ".json")

        frozen = jsonpickle.encode(self.exercise)
        with open(str(save_path), "w") as f:
            f.write(frozen)

    def pushButton_loadProject_clicked(self):
        print("load button clicked")
        project_filename = QFileDialog.getOpenFileName(filter="(*.json)")[0]
        project_dir = os.path.dirname(project_filename)
        project_name = os.path.splitext(os.path.basename(project_filename))[0]
        if project_dir is None or project_dir == "":
            return

        self.lineEdit_projectName.setText(project_name)
        self.pushButton_selectScene.setEnabled(True)

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

                # select just the scenes which are relevant for this exercise
                if len(scene.get_all_annotations()) == 1 and isinstance(scene.get_all_annotations()[0],
                                                                        CurveAnnotation):
                    item = QStandardItem()
                    item.setText(scene.name)
                    model.appendRow(item)

        self.listWidget_scenes.setModel(model)

    def pushButton_selectScene_clicked(self):
        index = self.listWidget_scenes.currentIndex()
        selected = index.data()
        self.lineEdit_selectedScenes.setText(selected)
        for scene in self.__scenes:
            if scene.name == selected:
                self.exercise.set_scene(scene)

    def setup_constraints(self):
        # TODO: uncomment constraints at the end
        # self.scene.registerField("lineEdit_selectedScenes*", self.lineEdit_selectedScenes)
        # self.target_value.registerField("lineEdit_error_beg*", self.lineEdit_error_beg)
        # self.target_value.registerField("lineEdit_time_beg*", self.lineEdit_time_beg)
        # self.target_value.registerField("lineEdit_errorWeighted_beg*", self.lineEdit_errorWeighted_beg)
        # self.target_value.registerField("lineEdit_timeWeighted_beg*", self.lineEdit_timeWeighted_beg)
        # self.target_value.registerField("lineEdit_error_int*", self.lineEdit_error_int)
        # self.target_value.registerField("lineEdit_time_int*", self.lineEdit_time_int)
        # self.target_value.registerField("lineEdit_errorWeighted_int*", self.lineEdit_errorWeighted_int)
        # self.target_value.registerField("lineEdit_timeWeighted_int*", self.lineEdit_timeWeighted_int)
        # self.target_value.registerField("lineEdit_error_com*", self.lineEdit_error_com)
        # self.target_value.registerField("lineEdit_time_com*", self.lineEdit_time_com)
        # self.target_value.registerField("lineEdit_errorWeighted_com*", self.lineEdit_errorWeighted_com)
        # self.target_value.registerField("lineEdit_timeWeighted_com*", self.lineEdit_timeWeighted_com)
        # self.feedback.registerField("lineEdit_goodTo*", self.lineEdit_goodTo)
        # self.feedback.registerField("lineEdit_goodFrom*", self.lineEdit_goodFrom)
        # self.feedback.registerField("lineEdit_averageTo*", self.lineEdit_averageTo)
        # self.feedback.registerField("lineEdit_averageFrom*", self.lineEdit_averageFrom)
        # self.feedback.registerField("lineEdit_badTo*", self.lineEdit_badTo)
        # self.feedback.registerField("lineEdit_badFrom*", self.lineEdit_badFrom)
        # self.feedback.registerField("lineEdit_exerciseName*",self.lineEdit_exerciseName)

        self.lineEdit_projectName.setEnabled(False)
        self.lineEdit_selectedScenes.setEnabled(False)
        self.pushButton_selectScene.setEnabled(False)
        self.lineEdit_weighted_beg.setEnabled(False)
        self.lineEdit_weighted_int.setEnabled(False)
        self.lineEdit_weighted_com.setEnabled(False)
        self.radioButton_error.setChecked(True)

    #  changes: QListWidget to QListView
    def setup_ui(self, Wizard):
        Wizard.setObjectName("Wizard")
        Wizard.resize(242, 350)
        self.scene = QtWidgets.QWizardPage()
        self.scene.setObjectName("scene")
        self.gridLayout = QtWidgets.QGridLayout(self.scene)
        self.gridLayout.setObjectName("gridLayout")
        self.label_projectName = QtWidgets.QLabel(self.scene)
        self.label_projectName.setObjectName("label_projectName")
        self.gridLayout.addWidget(self.label_projectName, 0, 0, 1, 2)
        self.lineEdit_projectName = QtWidgets.QLineEdit(self.scene)
        self.lineEdit_projectName.setObjectName("lineEdit_projectName")
        self.gridLayout.addWidget(self.lineEdit_projectName, 0, 2, 1, 1)
        self.pushButton_loadProject = QtWidgets.QPushButton(self.scene)
        self.pushButton_loadProject.setObjectName("pushButton_loadProject")
        self.gridLayout.addWidget(self.pushButton_loadProject, 0, 3, 1, 1)
        self.label_scenes = QtWidgets.QLabel(self.scene)
        self.label_scenes.setObjectName("label_scenes")
        self.gridLayout.addWidget(self.label_scenes, 1, 0, 1, 1)
        self.listWidget_scenes = QtWidgets.QListView(self.scene)
        self.listWidget_scenes.setObjectName("listWidget_scenes")
        self.gridLayout.addWidget(self.listWidget_scenes, 1, 1, 1, 3)
        self.pushButton_selectScene = QtWidgets.QPushButton(self.scene)
        self.pushButton_selectScene.setObjectName("pushButton_selectScene")
        self.gridLayout.addWidget(self.pushButton_selectScene, 2, 3, 1, 1)
        self.label_selected = QtWidgets.QLabel(self.scene)
        self.label_selected.setObjectName("label_selected")
        self.gridLayout.addWidget(self.label_selected, 3, 0, 1, 2)
        self.lineEdit_selectedScenes = QtWidgets.QLineEdit(self.scene)
        self.lineEdit_selectedScenes.setObjectName("lineEdit_selectedScenes")
        self.gridLayout.addWidget(self.lineEdit_selectedScenes, 3, 2, 1, 2)
        Wizard.addPage(self.scene)
        self.target_value = QtWidgets.QWizardPage()
        self.target_value.setObjectName("target_value")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.target_value)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.label_skillLevel = QtWidgets.QLabel(self.target_value)
        self.label_skillLevel.setObjectName("label_skillLevel")
        self.gridLayout_2.addWidget(self.label_skillLevel, 0, 0, 1, 2)
        self.label_error = QtWidgets.QLabel(self.target_value)
        self.label_error.setObjectName("label_error")
        self.gridLayout_2.addWidget(self.label_error, 1, 0, 1, 1)
        self.lineEdit_error_beg = QtWidgets.QLineEdit(self.target_value)
        self.lineEdit_error_beg.setObjectName("lineEdit_error_beg")
        self.gridLayout_2.addWidget(self.lineEdit_error_beg, 1, 1, 1, 1)
        self.label_time = QtWidgets.QLabel(self.target_value)
        self.label_time.setObjectName("label_time")
        self.gridLayout_2.addWidget(self.label_time, 1, 2, 1, 1)
        self.label_weighted = QtWidgets.QLabel(self.target_value)
        self.label_weighted.setObjectName("label_weighted")
        self.gridLayout_2.addWidget(self.label_weighted, 2, 0, 1, 3)
        self.label_error_weighted = QtWidgets.QLabel(self.target_value)
        self.label_error_weighted.setObjectName("label_error_weighted")
        self.gridLayout_2.addWidget(self.label_error_weighted, 3, 0, 1, 1)
        self.lineEdit_errorWeighted_beg = QtWidgets.QLineEdit(self.target_value)
        self.lineEdit_errorWeighted_beg.setObjectName("lineEdit_errorWeighted_beg")
        self.gridLayout_2.addWidget(self.lineEdit_errorWeighted_beg, 3, 1, 1, 1)
        self.label_time_weighted = QtWidgets.QLabel(self.target_value)
        self.label_time_weighted.setObjectName("label_time_weighted")
        self.gridLayout_2.addWidget(self.label_time_weighted, 3, 2, 1, 1)
        self.lineEdit_timeWeighted_beg = QtWidgets.QLineEdit(self.target_value)
        self.lineEdit_timeWeighted_beg.setObjectName("lineEdit_timeWeighted_beg")
        self.gridLayout_2.addWidget(self.lineEdit_timeWeighted_beg, 3, 3, 1, 1)
        self.lineEdit_weighted_beg = QtWidgets.QLineEdit(self.target_value)
        self.lineEdit_weighted_beg.setObjectName("lineEdit_weighted_beg")
        self.gridLayout_2.addWidget(self.lineEdit_weighted_beg, 3, 4, 1, 1)
        self.label_skillLevel_2 = QtWidgets.QLabel(self.target_value)
        self.label_skillLevel_2.setObjectName("label_skillLevel_2")
        self.gridLayout_2.addWidget(self.label_skillLevel_2, 4, 0, 1, 2)
        self.label_error_2 = QtWidgets.QLabel(self.target_value)
        self.label_error_2.setObjectName("label_error_2")
        self.gridLayout_2.addWidget(self.label_error_2, 5, 0, 1, 1)
        self.lineEdit_error_int = QtWidgets.QLineEdit(self.target_value)
        self.lineEdit_error_int.setObjectName("lineEdit_error_int")
        self.gridLayout_2.addWidget(self.lineEdit_error_int, 5, 1, 1, 1)
        self.label_time_2 = QtWidgets.QLabel(self.target_value)
        self.label_time_2.setObjectName("label_time_2")
        self.gridLayout_2.addWidget(self.label_time_2, 5, 2, 1, 1)
        self.label_weighted_2 = QtWidgets.QLabel(self.target_value)
        self.label_weighted_2.setObjectName("label_weighted_2")
        self.gridLayout_2.addWidget(self.label_weighted_2, 6, 0, 1, 3)
        self.label_error_weighted_2 = QtWidgets.QLabel(self.target_value)
        self.label_error_weighted_2.setObjectName("label_error_weighted_2")
        self.gridLayout_2.addWidget(self.label_error_weighted_2, 7, 0, 1, 1)
        self.lineEdit_errorWeighted_int = QtWidgets.QLineEdit(self.target_value)
        self.lineEdit_errorWeighted_int.setObjectName("lineEdit_errorWeighted_int")
        self.gridLayout_2.addWidget(self.lineEdit_errorWeighted_int, 7, 1, 1, 1)
        self.label_time_weighted_2 = QtWidgets.QLabel(self.target_value)
        self.label_time_weighted_2.setObjectName("label_time_weighted_2")
        self.gridLayout_2.addWidget(self.label_time_weighted_2, 7, 2, 1, 1)
        self.lineEdit_timeWeighted_int = QtWidgets.QLineEdit(self.target_value)
        self.lineEdit_timeWeighted_int.setObjectName("lineEdit_timeWeighted_int")
        self.gridLayout_2.addWidget(self.lineEdit_timeWeighted_int, 7, 3, 1, 1)
        self.lineEdit_weighted_int = QtWidgets.QLineEdit(self.target_value)
        self.lineEdit_weighted_int.setObjectName("lineEdit_weighted_int")
        self.gridLayout_2.addWidget(self.lineEdit_weighted_int, 7, 4, 1, 1)
        self.label_skillLevel_3 = QtWidgets.QLabel(self.target_value)
        self.label_skillLevel_3.setObjectName("label_skillLevel_3")
        self.gridLayout_2.addWidget(self.label_skillLevel_3, 8, 0, 1, 2)
        self.label_error_3 = QtWidgets.QLabel(self.target_value)
        self.label_error_3.setObjectName("label_error_3")
        self.gridLayout_2.addWidget(self.label_error_3, 9, 0, 1, 1)
        self.lineEdit_error_com = QtWidgets.QLineEdit(self.target_value)
        self.lineEdit_error_com.setObjectName("lineEdit_error_com")
        self.gridLayout_2.addWidget(self.lineEdit_error_com, 9, 1, 1, 1)
        self.label_time_3 = QtWidgets.QLabel(self.target_value)
        self.label_time_3.setObjectName("label_time_3")
        self.gridLayout_2.addWidget(self.label_time_3, 9, 2, 1, 1)
        self.label_weighted_3 = QtWidgets.QLabel(self.target_value)
        self.label_weighted_3.setObjectName("label_weighted_3")
        self.gridLayout_2.addWidget(self.label_weighted_3, 10, 0, 1, 3)
        self.label_error_weighted_3 = QtWidgets.QLabel(self.target_value)
        self.label_error_weighted_3.setObjectName("label_error_weighted_3")
        self.gridLayout_2.addWidget(self.label_error_weighted_3, 11, 0, 1, 1)
        self.lineEdit_errorWeighted_com = QtWidgets.QLineEdit(self.target_value)
        self.lineEdit_errorWeighted_com.setObjectName("lineEdit_errorWeighted_com")
        self.gridLayout_2.addWidget(self.lineEdit_errorWeighted_com, 11, 1, 1, 1)
        self.label_time_weighted_3 = QtWidgets.QLabel(self.target_value)
        self.label_time_weighted_3.setObjectName("label_time_weighted_3")
        self.gridLayout_2.addWidget(self.label_time_weighted_3, 11, 2, 1, 1)
        self.lineEdit_timeWeighted_com = QtWidgets.QLineEdit(self.target_value)
        self.lineEdit_timeWeighted_com.setObjectName("lineEdit_timeWeighted_com")
        self.gridLayout_2.addWidget(self.lineEdit_timeWeighted_com, 11, 3, 1, 1)
        self.lineEdit_weighted_com = QtWidgets.QLineEdit(self.target_value)
        self.lineEdit_weighted_com.setObjectName("lineEdit_weighted_com")
        self.gridLayout_2.addWidget(self.lineEdit_weighted_com, 11, 4, 1, 1)
        self.lineEdit_time_int = QtWidgets.QLineEdit(self.target_value)
        self.lineEdit_time_int.setObjectName("lineEdit_time_int")
        self.gridLayout_2.addWidget(self.lineEdit_time_int, 4, 3, 3, 1)
        self.lineEdit_time_com = QtWidgets.QLineEdit(self.target_value)
        self.lineEdit_time_com.setObjectName("lineEdit_time_com")
        self.gridLayout_2.addWidget(self.lineEdit_time_com, 8, 3, 3, 1)
        self.lineEdit_time_beg = QtWidgets.QLineEdit(self.target_value)
        self.lineEdit_time_beg.setObjectName("lineEdit_time_beg")
        self.gridLayout_2.addWidget(self.lineEdit_time_beg, 0, 3, 3, 1)
        Wizard.addPage(self.target_value)
        self.feedback = QtWidgets.QWizardPage()
        self.feedback.setObjectName("feedback")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.feedback)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.label_aspect = QtWidgets.QLabel(self.feedback)
        self.label_aspect.setObjectName("label_aspect")
        self.gridLayout_3.addWidget(self.label_aspect, 0, 0, 1, 5)
        self.radioButton_error = QtWidgets.QRadioButton(self.feedback)
        self.radioButton_error.setObjectName("radioButton_error")
        self.gridLayout_3.addWidget(self.radioButton_error, 1, 0, 1, 2)
        self.radioButton_time = QtWidgets.QRadioButton(self.feedback)
        self.radioButton_time.setObjectName("radioButton_time")
        self.gridLayout_3.addWidget(self.radioButton_time, 2, 0, 1, 2)
        self.radioButton_weighted = QtWidgets.QRadioButton(self.feedback)
        self.radioButton_weighted.setObjectName("radioButton_weighted")
        self.gridLayout_3.addWidget(self.radioButton_weighted, 3, 0, 1, 3)
        self.label_good = QtWidgets.QLabel(self.feedback)
        self.label_good.setObjectName("label_good")
        self.gridLayout_3.addWidget(self.label_good, 4, 0, 1, 1)
        self.label_from_1 = QtWidgets.QLabel(self.feedback)
        self.label_from_1.setObjectName("label_from_1")
        self.gridLayout_3.addWidget(self.label_from_1, 4, 1, 1, 1)
        self.lineEdit_goodFrom = QtWidgets.QLineEdit(self.feedback)
        self.lineEdit_goodFrom.setObjectName("lineEdit_goodFrom")
        self.gridLayout_3.addWidget(self.lineEdit_goodFrom, 4, 2, 1, 1)
        self.label_to_1 = QtWidgets.QLabel(self.feedback)
        self.label_to_1.setObjectName("label_to_1")
        self.gridLayout_3.addWidget(self.label_to_1, 4, 3, 1, 1)
        self.lineEdit_goodTo = QtWidgets.QLineEdit(self.feedback)
        self.lineEdit_goodTo.setObjectName("lineEdit_goodTo")
        self.gridLayout_3.addWidget(self.lineEdit_goodTo, 4, 4, 1, 1)
        self.label_average = QtWidgets.QLabel(self.feedback)
        self.label_average.setObjectName("label_average")
        self.gridLayout_3.addWidget(self.label_average, 5, 0, 1, 1)
        self.label_from_2 = QtWidgets.QLabel(self.feedback)
        self.label_from_2.setObjectName("label_from_2")
        self.gridLayout_3.addWidget(self.label_from_2, 5, 1, 1, 1)
        self.lineEdit_averageFrom = QtWidgets.QLineEdit(self.feedback)
        self.lineEdit_averageFrom.setObjectName("lineEdit_averageFrom")
        self.gridLayout_3.addWidget(self.lineEdit_averageFrom, 5, 2, 1, 1)
        self.label_to_2 = QtWidgets.QLabel(self.feedback)
        self.label_to_2.setObjectName("label_to_2")
        self.gridLayout_3.addWidget(self.label_to_2, 5, 3, 1, 1)
        self.lineEdit_averageTo = QtWidgets.QLineEdit(self.feedback)
        self.lineEdit_averageTo.setObjectName("lineEdit_averageTo")
        self.gridLayout_3.addWidget(self.lineEdit_averageTo, 5, 4, 1, 1)
        self.label_bad = QtWidgets.QLabel(self.feedback)
        self.label_bad.setObjectName("label_bad")
        self.gridLayout_3.addWidget(self.label_bad, 6, 0, 1, 1)
        self.label_from_3 = QtWidgets.QLabel(self.feedback)
        self.label_from_3.setObjectName("label_from_3")
        self.gridLayout_3.addWidget(self.label_from_3, 6, 1, 1, 1)
        self.lineEdit_badFrom = QtWidgets.QLineEdit(self.feedback)
        self.lineEdit_badFrom.setObjectName("lineEdit_badFrom")
        self.gridLayout_3.addWidget(self.lineEdit_badFrom, 6, 2, 1, 1)
        self.label_to_3 = QtWidgets.QLabel(self.feedback)
        self.label_to_3.setObjectName("label_to_3")
        self.gridLayout_3.addWidget(self.label_to_3, 6, 3, 1, 1)
        self.lineEdit_badTo = QtWidgets.QLineEdit(self.feedback)
        self.lineEdit_badTo.setObjectName("lineEdit_badTo")
        self.gridLayout_3.addWidget(self.lineEdit_badTo, 6, 4, 1, 1)
        self.label_exerciseName = QtWidgets.QLabel(self.feedback)
        self.label_exerciseName.setObjectName("label_exerciseName")
        self.gridLayout_3.addWidget(self.label_exerciseName, 7, 0, 1, 3)
        self.lineEdit_exerciseName = QtWidgets.QLineEdit(self.feedback)
        self.lineEdit_exerciseName.setObjectName("lineEdit_exerciseName")
        self.gridLayout_3.addWidget(self.lineEdit_exerciseName, 8, 0, 1, 3)
        Wizard.addPage(self.feedback)

        self.retranslateUi(Wizard)
        QtCore.QMetaObject.connectSlotsByName(Wizard)

    def retranslateUi(self, Wizard):
        _translate = QtCore.QCoreApplication.translate
        Wizard.setWindowTitle(_translate("Wizard", "Wizard"))
        self.label_projectName.setText(_translate("Wizard", "Project name:"))
        self.pushButton_loadProject.setText(_translate("Wizard", "Load project"))
        self.label_scenes.setText(_translate("Wizard", "Scenes:"))
        self.pushButton_selectScene.setText(_translate("Wizard", "Select"))
        self.label_selected.setText(_translate("Wizard", "Selected scene:"))
        self.label_skillLevel.setText(_translate("Wizard", "Skill level beginner:"))
        self.label_error.setText(_translate("Wizard", "Error:"))
        self.label_time.setText(_translate("Wizard", "Time:"))
        self.label_weighted.setText(_translate("Wizard", "Weighted combination:"))
        self.label_error_weighted.setText(_translate("Wizard", "Error:"))
        self.label_time_weighted.setText(_translate("Wizard", "Time:"))
        self.label_skillLevel_2.setText(_translate("Wizard", "Skill level intermediate:"))
        self.label_error_2.setText(_translate("Wizard", "Error:"))
        self.label_time_2.setText(_translate("Wizard", "Time:"))
        self.label_weighted_2.setText(_translate("Wizard", "Weighted combination:"))
        self.label_error_weighted_2.setText(_translate("Wizard", "Error:"))
        self.label_time_weighted_2.setText(_translate("Wizard", "Time:"))
        self.label_skillLevel_3.setText(_translate("Wizard", "Skill level competent:"))
        self.label_error_3.setText(_translate("Wizard", "Error:"))
        self.label_time_3.setText(_translate("Wizard", "Time:"))
        self.label_weighted_3.setText(_translate("Wizard", "Weighted combination:"))
        self.label_error_weighted_3.setText(_translate("Wizard", "Error:"))
        self.label_time_weighted_3.setText(_translate("Wizard", "Time:"))
        self.label_aspect.setText(_translate("Wizard", "Aspect for the given the feedback:"))
        self.radioButton_error.setText(_translate("Wizard", "Error"))
        self.radioButton_time.setText(_translate("Wizard", "Time"))
        self.radioButton_weighted.setText(_translate("Wizard", "Weighted combination"))
        self.label_good.setText(_translate("Wizard", "Good:"))
        self.label_from_1.setText(_translate("Wizard", "from"))
        self.label_to_1.setText(_translate("Wizard", "to"))
        self.label_average.setText(_translate("Wizard", "Average:"))
        self.label_from_2.setText(_translate("Wizard", "from"))
        self.label_to_2.setText(_translate("Wizard", "to"))
        self.label_bad.setText(_translate("Wizard", "Bad:"))
        self.label_from_3.setText(_translate("Wizard", "from"))
        self.label_to_3.setText(_translate("Wizard", "to"))
        self.label_exerciseName.setText(_translate("Wizard", "Name of the exercise:"))
