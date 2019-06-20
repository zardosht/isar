from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QMainWindow


class HandSkillExerciseExecution(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setup_ui(self)
        self.setup_signals()
        self.setup_constraints()
        self.setup_models()

        self.setWindowTitle("Handskill Exercise Execution")

    def setup_signals(self):
        self.button_calibrate_projector.clicked.connect(self.calibrate_projector)
        self.button_init_scene_size.clicked.connect(self.init_scene_size)
        self.button_load_project.clicked.connect(self.load_project)
        self.button_select_exercise.clicked.connect(self.select_exercise)
        self.button_start.clicked.connect(self.start_exercise)

    def setup_models(self):
        pass

    def calibrate_projector(self):
        print("calibrate projector")

    def init_scene_size(self):
        print("init scene size")

    def load_project(self):
        print("load button")

    def select_exercise(self):
        print("select exercise")

    def start_exercise(self):
        print("start")

    def setup_constraints(self):
        self.line_project_name.setEnabled(False)
        self.line_selected_exercises.setEnabled(False)
        self.radio_button_beginner.setChecked(True)


    def setup_ui(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(400, 500)

        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.label_project_name = QtWidgets.QLabel(self.centralwidget)
        self.label_project_name.setObjectName("label_project_name")
        self.gridLayout.addWidget(self.label_project_name, 1, 0, 1, 1)
        self.label_exercise = QtWidgets.QLabel(self.centralwidget)
        self.label_exercise.setObjectName("label_exercise")
        self.gridLayout.addWidget(self.label_exercise, 2, 0, 1, 1)
        self.line_selected_exercises = QtWidgets.QLineEdit(self.centralwidget)
        self.line_selected_exercises.setObjectName("line_selected_exercises")
        self.gridLayout.addWidget(self.line_selected_exercises, 3, 1, 1, 4)
        self.radio_button_intermediate = QtWidgets.QRadioButton(self.centralwidget)
        self.radio_button_intermediate.setObjectName("radio_button_intermediate")
        self.gridLayout.addWidget(self.radio_button_intermediate, 4, 2, 1, 3)
        self.list_exercises = QtWidgets.QListView(self.centralwidget)
        self.list_exercises.setObjectName("list_exercises")
        self.gridLayout.addWidget(self.list_exercises, 2, 1, 1, 5)
        self.radio_button_competent = QtWidgets.QRadioButton(self.centralwidget)
        self.radio_button_competent.setObjectName("radio_button_competent")
        self.gridLayout.addWidget(self.radio_button_competent, 4, 5, 1, 1)
        self.button_select_exercise = QtWidgets.QPushButton(self.centralwidget)
        self.button_select_exercise.setObjectName("button_select_exercise")
        self.gridLayout.addWidget(self.button_select_exercise, 3, 5, 1, 1)
        self.radio_button_beginner = QtWidgets.QRadioButton(self.centralwidget)
        self.radio_button_beginner.setObjectName("radio_button_beginner")
        self.gridLayout.addWidget(self.radio_button_beginner, 4, 1, 1, 1)
        self.button_start = QtWidgets.QPushButton(self.centralwidget)
        self.button_start.setObjectName("button_start")
        self.gridLayout.addWidget(self.button_start, 5, 1, 1, 5)
        self.label_skill_level = QtWidgets.QLabel(self.centralwidget)
        self.label_skill_level.setObjectName("label_skill_level")
        self.gridLayout.addWidget(self.label_skill_level, 4, 0, 1, 1)
        self.label_selected = QtWidgets.QLabel(self.centralwidget)
        self.label_selected.setObjectName("label_selected")
        self.gridLayout.addWidget(self.label_selected, 3, 0, 1, 1)
        self.button_calibrate_projector = QtWidgets.QPushButton(self.centralwidget)
        self.button_calibrate_projector.setObjectName("button_calibrate_projector")
        self.gridLayout.addWidget(self.button_calibrate_projector, 0, 0, 1, 2)
        self.button_load_project = QtWidgets.QPushButton(self.centralwidget)
        self.button_load_project.setObjectName("button_load_project")
        self.gridLayout.addWidget(self.button_load_project, 1, 5, 1, 1)
        self.line_project_name = QtWidgets.QLineEdit(self.centralwidget)
        self.line_project_name.setObjectName("line_project_name")
        self.gridLayout.addWidget(self.line_project_name, 1, 1, 1, 4)
        self.button_init_scene_size = QtWidgets.QPushButton(self.centralwidget)
        self.button_init_scene_size.setObjectName("button_init_scene_size")
        self.gridLayout.addWidget(self.button_init_scene_size, 0, 3, 1, 3)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 284, 17))
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
        self.label_project_name.setText(_translate("MainWindow", "Project name:"))
        self.label_exercise.setText(_translate("MainWindow", "Exercise:"))
        self.radio_button_intermediate.setText(_translate("MainWindow", "Intermediate"))
        self.radio_button_competent.setText(_translate("MainWindow", "Competent"))
        self.button_select_exercise.setText(_translate("MainWindow", "Select"))
        self.radio_button_beginner.setText(_translate("MainWindow", "Beginner"))
        self.button_start.setText(_translate("MainWindow", "Start"))
        self.label_skill_level.setText(_translate("MainWindow", "Skill level:"))
        self.label_selected.setText(_translate("MainWindow", "Selected exercise:"))
        self.button_calibrate_projector.setText(_translate("MainWindow", "Calibrate Projector"))
        self.button_load_project.setText(_translate("MainWindow", "Load project"))
        self.button_init_scene_size.setText(_translate("MainWindow", "Init Scene Size"))
