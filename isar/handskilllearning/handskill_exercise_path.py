import os

import jsonpickle
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QWizard, QFileDialog

from isar.scene.annotationmodel import CurveAnnotation
from isar.scene.scenemodel import ScenesModel


class HandSkillExercisePath(QWizard):

    def __init__(self):
        super().__init__()
        self.setup_ui(self)
        self.setup_signals()
        self.scenes_model = ScenesModel()
        self.__scenes = None

    def setup_signals(self):
        self.pushButton_loadProject.clicked.connect(self.pushButton_loadProject_clicked)
        self.pushButton_selectScene.clicked.connect(self.pushButton_selectScene_clicked)

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
                if len(scene.get_all_annotations()) == 1 and isinstance(scene.get_all_annotations()[0], CurveAnnotation):
                    item = QStandardItem()
                    item.setText(scene.name)
                    model.appendRow(item)

        self.listWidget_scenes.setModel(model)


    def pushButton_selectScene_clicked(self):
        index = self.listWidget_scenes.currentIndex()
        selected = index.data()
        self.lineEdit_selectedScenes.setText(selected)


    def setup_ui(self, Wizard):
        Wizard.setObjectName("Wizard")
        Wizard.resize(295, 248)
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
        self.gridLayout_2.addWidget(self.label_skillLevel, 0, 0, 1, 3)
        self.comboBox_skillLevel = QtWidgets.QComboBox(self.target_value)
        self.comboBox_skillLevel.setObjectName("comboBox_skillLevel")
        self.comboBox_skillLevel.addItem("")
        self.comboBox_skillLevel.addItem("")
        self.comboBox_skillLevel.addItem("")
        self.gridLayout_2.addWidget(self.comboBox_skillLevel, 0, 3, 1, 4)
        self.label_error = QtWidgets.QLabel(self.target_value)
        self.label_error.setObjectName("label_error")
        self.gridLayout_2.addWidget(self.label_error, 1, 0, 1, 2)
        self.lineEdit_error = QtWidgets.QLineEdit(self.target_value)
        self.lineEdit_error.setObjectName("lineEdit_error")
        self.gridLayout_2.addWidget(self.lineEdit_error, 1, 2, 1, 2)
        self.label_time = QtWidgets.QLabel(self.target_value)
        self.label_time.setObjectName("label_time")
        self.gridLayout_2.addWidget(self.label_time, 2, 0, 1, 2)
        self.lineEdit_time = QtWidgets.QLineEdit(self.target_value)
        self.lineEdit_time.setObjectName("lineEdit_time")
        self.gridLayout_2.addWidget(self.lineEdit_time, 2, 2, 1, 2)
        self.label_weighted = QtWidgets.QLabel(self.target_value)
        self.label_weighted.setObjectName("label_weighted")
        self.gridLayout_2.addWidget(self.label_weighted, 3, 0, 1, 6)
        self.label_error_weighted = QtWidgets.QLabel(self.target_value)
        self.label_error_weighted.setObjectName("label_error_weighted")
        self.gridLayout_2.addWidget(self.label_error_weighted, 4, 0, 1, 1)
        self.lineEdit_errorWeighted = QtWidgets.QLineEdit(self.target_value)
        self.lineEdit_errorWeighted.setObjectName("lineEdit_errorWeighted")
        self.gridLayout_2.addWidget(self.lineEdit_errorWeighted, 4, 1, 1, 3)
        self.label_time_weighted = QtWidgets.QLabel(self.target_value)
        self.label_time_weighted.setObjectName("label_time_weighted")
        self.gridLayout_2.addWidget(self.label_time_weighted, 4, 4, 1, 1)
        self.lineEdit_timeWeighted = QtWidgets.QLineEdit(self.target_value)
        self.lineEdit_timeWeighted.setObjectName("lineEdit_timeWeighted")
        self.gridLayout_2.addWidget(self.lineEdit_timeWeighted, 4, 5, 1, 1)
        self.lineEdit_weighted = QtWidgets.QLineEdit(self.target_value)
        self.lineEdit_weighted.setObjectName("lineEdit_weighted")
        self.gridLayout_2.addWidget(self.lineEdit_weighted, 4, 6, 1, 1)
        Wizard.addPage(self.target_value)

        self.feedback = QtWidgets.QWizardPage()
        self.feedback.setObjectName("feedback")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.feedback)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.label_aspect = QtWidgets.QLabel(self.feedback)
        self.label_aspect.setObjectName("label_aspect")
        self.gridLayout_3.addWidget(self.label_aspect, 0, 0, 1, 1)
        self.comboBox_feedback = QtWidgets.QComboBox(self.feedback)
        self.comboBox_feedback.setObjectName("comboBox_feedback")
        self.comboBox_feedback.addItem("")
        self.comboBox_feedback.addItem("")
        self.comboBox_feedback.addItem("")
        self.gridLayout_3.addWidget(self.comboBox_feedback, 0, 1, 1, 4)
        self.label_good = QtWidgets.QLabel(self.feedback)
        self.label_good.setObjectName("label_good")
        self.gridLayout_3.addWidget(self.label_good, 1, 0, 1, 1)
        self.label_from_1 = QtWidgets.QLabel(self.feedback)
        self.label_from_1.setObjectName("label_from_1")
        self.gridLayout_3.addWidget(self.label_from_1, 1, 1, 1, 1)
        self.lineEdit_goodFrom = QtWidgets.QLineEdit(self.feedback)
        self.lineEdit_goodFrom.setObjectName("lineEdit_goodFrom")
        self.gridLayout_3.addWidget(self.lineEdit_goodFrom, 1, 2, 1, 1)
        self.label_to_1 = QtWidgets.QLabel(self.feedback)
        self.label_to_1.setObjectName("label_to_1")
        self.gridLayout_3.addWidget(self.label_to_1, 1, 3, 1, 1)
        self.lineEdit_goodTo = QtWidgets.QLineEdit(self.feedback)
        self.lineEdit_goodTo.setObjectName("lineEdit_goodTo")
        self.gridLayout_3.addWidget(self.lineEdit_goodTo, 1, 4, 1, 1)
        self.label_average = QtWidgets.QLabel(self.feedback)
        self.label_average.setObjectName("label_average")
        self.gridLayout_3.addWidget(self.label_average, 2, 0, 1, 1)
        self.label_from_2 = QtWidgets.QLabel(self.feedback)
        self.label_from_2.setObjectName("label_from_2")
        self.gridLayout_3.addWidget(self.label_from_2, 2, 1, 1, 1)
        self.lineEdit_averageFrom = QtWidgets.QLineEdit(self.feedback)
        self.lineEdit_averageFrom.setObjectName("lineEdit_averageFrom")
        self.gridLayout_3.addWidget(self.lineEdit_averageFrom, 2, 2, 1, 1)
        self.label_to_2 = QtWidgets.QLabel(self.feedback)
        self.label_to_2.setObjectName("label_to_2")
        self.gridLayout_3.addWidget(self.label_to_2, 2, 3, 1, 1)
        self.lineEdit_averageTo = QtWidgets.QLineEdit(self.feedback)
        self.lineEdit_averageTo.setObjectName("lineEdit_averageTo")
        self.gridLayout_3.addWidget(self.lineEdit_averageTo, 2, 4, 1, 1)
        self.label_bad = QtWidgets.QLabel(self.feedback)
        self.label_bad.setObjectName("label_bad")
        self.gridLayout_3.addWidget(self.label_bad, 3, 0, 1, 1)
        self.label_from_3 = QtWidgets.QLabel(self.feedback)
        self.label_from_3.setObjectName("label_from_3")
        self.gridLayout_3.addWidget(self.label_from_3, 3, 1, 1, 1)
        self.lineEdit_badFrom = QtWidgets.QLineEdit(self.feedback)
        self.lineEdit_badFrom.setObjectName("lineEdit_badFrom")
        self.gridLayout_3.addWidget(self.lineEdit_badFrom, 3, 2, 1, 1)
        self.label_to_3 = QtWidgets.QLabel(self.feedback)
        self.label_to_3.setObjectName("label_to_3")
        self.gridLayout_3.addWidget(self.label_to_3, 3, 3, 1, 1)
        self.lineEdit_badTo = QtWidgets.QLineEdit(self.feedback)
        self.lineEdit_badTo.setObjectName("lineEdit_badTo")
        self.gridLayout_3.addWidget(self.lineEdit_badTo, 3, 4, 1, 1)
        Wizard.addPage(self.feedback)

        self.scene.registerField("lineEdit_selectedScenes*", self.lineEdit_selectedScenes)
        self.target_value.registerField("lineEdit_weighted*", self.lineEdit_weighted)
        self.feedback.registerField("lineEdit_badTo*", self.lineEdit_badTo)

        self.lineEdit_projectName.setEnabled(False)
        self.lineEdit_selectedScenes.setEnabled(False)
        self.pushButton_selectScene.setEnabled(False)

        self.retranslate_ui(Wizard)
        QtCore.QMetaObject.connectSlotsByName(Wizard)


    def retranslate_ui(self, Wizard):
        _translate = QtCore.QCoreApplication.translate
        Wizard.setWindowTitle(_translate("Wizard", "Wizard"))
        self.label_projectName.setText(_translate("Wizard", "Project name:"))
        self.pushButton_loadProject.setText(_translate("Wizard", "Load project"))
        self.label_scenes.setText(_translate("Wizard", "Scenes:"))
        self.pushButton_selectScene.setText(_translate("Wizard", "Select"))
        self.label_selected.setText(_translate("Wizard", "Selected scene:"))
        self.label_skillLevel.setText(_translate("Wizard", "Skill level:"))
        self.comboBox_skillLevel.setItemText(0, _translate("Wizard", "Beginner"))
        self.comboBox_skillLevel.setItemText(1, _translate("Wizard", "Intermediate"))
        self.comboBox_skillLevel.setItemText(2, _translate("Wizard", "Competent"))
        self.label_error.setText(_translate("Wizard", "Error:"))
        self.label_time.setText(_translate("Wizard", "Time:"))
        self.label_weighted.setText(_translate("Wizard", "Weighted combination:"))
        self.label_error_weighted.setText(_translate("Wizard", "Error:"))
        self.label_time_weighted.setText(_translate("Wizard", "Time:"))
        self.label_aspect.setText(_translate("Wizard", "Aspect:"))
        self.comboBox_feedback.setItemText(0, _translate("Wizard", "Error"))
        self.comboBox_feedback.setItemText(1, _translate("Wizard", "Time"))
        self.comboBox_feedback.setItemText(2, _translate("Wizard", "Weighted combination"))
        self.label_good.setText(_translate("Wizard", "Good:"))
        self.label_from_1.setText(_translate("Wizard", "from"))
        self.label_to_1.setText(_translate("Wizard", "to"))
        self.label_average.setText(_translate("Wizard", "Average:"))
        self.label_from_2.setText(_translate("Wizard", "from"))
        self.label_to_2.setText(_translate("Wizard", "to"))
        self.label_bad.setText(_translate("Wizard", "Bad:"))
        self.label_from_3.setText(_translate("Wizard", "from"))
        self.label_to_3.setText(_translate("Wizard", "to"))


