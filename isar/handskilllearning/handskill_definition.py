from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QWidget


class HandskillDefinition(QWidget):

    def __init__(self):
        super().__init__()
        self.setupUi(self)

    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(741, 423)
        self.gridLayout_3 = QtWidgets.QGridLayout(Form)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.label_33 = QtWidgets.QLabel(Form)
        self.label_33.setObjectName("label_33")
        self.gridLayout.addWidget(self.label_33, 16, 1, 1, 2)
        self.label_29 = QtWidgets.QLabel(Form)
        self.label_29.setObjectName("label_29")
        self.gridLayout.addWidget(self.label_29, 7, 0, 1, 1)
        self.lineEdit_21 = QtWidgets.QLineEdit(Form)
        self.lineEdit_21.setObjectName("lineEdit_21")
        self.gridLayout.addWidget(self.lineEdit_21, 8, 3, 1, 2)
        self.lineEdit_5 = QtWidgets.QLineEdit(Form)
        self.lineEdit_5.setObjectName("lineEdit_5")
        self.gridLayout.addWidget(self.lineEdit_5, 5, 4, 1, 1)
        self.lineEdit_20 = QtWidgets.QLineEdit(Form)
        self.lineEdit_20.setObjectName("lineEdit_20")
        self.gridLayout.addWidget(self.lineEdit_20, 10, 3, 1, 1)
        self.label_36 = QtWidgets.QLabel(Form)
        self.label_36.setObjectName("label_36")
        self.gridLayout.addWidget(self.label_36, 17, 0, 1, 5)
        self.label_32 = QtWidgets.QLabel(Form)
        self.label_32.setObjectName("label_32")
        self.gridLayout.addWidget(self.label_32, 15, 1, 1, 2)
        self.label_7 = QtWidgets.QLabel(Form)
        self.label_7.setObjectName("label_7")
        self.gridLayout.addWidget(self.label_7, 2, 0, 1, 1)
        self.lineEdit_3 = QtWidgets.QLineEdit(Form)
        self.lineEdit_3.setObjectName("lineEdit_3")
        self.gridLayout.addWidget(self.lineEdit_3, 3, 3, 1, 2)
        self.lineEdit_18 = QtWidgets.QLineEdit(Form)
        self.lineEdit_18.setObjectName("lineEdit_18")
        self.gridLayout.addWidget(self.lineEdit_18, 10, 4, 1, 1)
        self.lineEdit_26 = QtWidgets.QLineEdit(Form)
        self.lineEdit_26.setObjectName("lineEdit_26")
        self.gridLayout.addWidget(self.lineEdit_26, 15, 3, 1, 1)
        self.lineEdit_15 = QtWidgets.QLineEdit(Form)
        self.lineEdit_15.setObjectName("lineEdit_15")
        self.gridLayout.addWidget(self.lineEdit_15, 6, 3, 1, 1)
        self.label_24 = QtWidgets.QLabel(Form)
        self.label_24.setObjectName("label_24")
        self.gridLayout.addWidget(self.label_24, 8, 1, 1, 2)
        self.label_25 = QtWidgets.QLabel(Form)
        self.label_25.setObjectName("label_25")
        self.gridLayout.addWidget(self.label_25, 7, 1, 1, 2)
        self.lineEdit_23 = QtWidgets.QLineEdit(Form)
        self.lineEdit_23.setObjectName("lineEdit_23")
        self.gridLayout.addWidget(self.lineEdit_23, 16, 4, 1, 1)
        self.lineEdit_27 = QtWidgets.QLineEdit(Form)
        self.lineEdit_27.setObjectName("lineEdit_27")
        self.gridLayout.addWidget(self.lineEdit_27, 13, 3, 1, 2)
        self.lineEdit_22 = QtWidgets.QLineEdit(Form)
        self.lineEdit_22.setObjectName("lineEdit_22")
        self.gridLayout.addWidget(self.lineEdit_22, 16, 3, 1, 1)
        self.lineEdit_16 = QtWidgets.QLineEdit(Form)
        self.lineEdit_16.setObjectName("lineEdit_16")
        self.gridLayout.addWidget(self.lineEdit_16, 11, 3, 1, 1)
        self.label_30 = QtWidgets.QLabel(Form)
        self.label_30.setObjectName("label_30")
        self.gridLayout.addWidget(self.label_30, 13, 1, 1, 2)
        self.label_22 = QtWidgets.QLabel(Form)
        self.label_22.setObjectName("label_22")
        self.gridLayout.addWidget(self.label_22, 6, 1, 1, 2)
        self.label_27 = QtWidgets.QLabel(Form)
        self.label_27.setObjectName("label_27")
        self.gridLayout.addWidget(self.label_27, 11, 1, 1, 2)
        self.lineEdit_25 = QtWidgets.QLineEdit(Form)
        self.lineEdit_25.setObjectName("lineEdit_25")
        self.gridLayout.addWidget(self.lineEdit_25, 12, 3, 1, 2)
        self.label_23 = QtWidgets.QLabel(Form)
        self.label_23.setObjectName("label_23")
        self.gridLayout.addWidget(self.label_23, 5, 1, 1, 2)
        self.lineEdit_14 = QtWidgets.QLineEdit(Form)
        self.lineEdit_14.setObjectName("lineEdit_14")
        self.gridLayout.addWidget(self.lineEdit_14, 6, 4, 1, 1)
        self.label_4 = QtWidgets.QLabel(Form)
        self.label_4.setObjectName("label_4")
        self.gridLayout.addWidget(self.label_4, 2, 1, 1, 2)
        self.label_31 = QtWidgets.QLabel(Form)
        self.label_31.setObjectName("label_31")
        self.gridLayout.addWidget(self.label_31, 12, 1, 1, 2)
        self.lineEdit = QtWidgets.QLineEdit(Form)
        self.lineEdit.setObjectName("lineEdit")
        self.gridLayout.addWidget(self.lineEdit, 0, 2, 1, 3)
        self.label_35 = QtWidgets.QLabel(Form)
        self.label_35.setObjectName("label_35")
        self.gridLayout.addWidget(self.label_35, 12, 0, 1, 1)
        self.lineEdit_17 = QtWidgets.QLineEdit(Form)
        self.lineEdit_17.setObjectName("lineEdit_17")
        self.gridLayout.addWidget(self.lineEdit_17, 11, 4, 1, 1)
        self.lineEdit_4 = QtWidgets.QLineEdit(Form)
        self.lineEdit_4.setObjectName("lineEdit_4")
        self.gridLayout.addWidget(self.lineEdit_4, 5, 3, 1, 1)
        self.lineEdit_19 = QtWidgets.QLineEdit(Form)
        self.lineEdit_19.setObjectName("lineEdit_19")
        self.gridLayout.addWidget(self.lineEdit_19, 7, 3, 1, 2)
        self.lineEdit_24 = QtWidgets.QLineEdit(Form)
        self.lineEdit_24.setObjectName("lineEdit_24")
        self.gridLayout.addWidget(self.lineEdit_24, 15, 4, 1, 1)
        self.label_26 = QtWidgets.QLabel(Form)
        self.label_26.setObjectName("label_26")
        self.gridLayout.addWidget(self.label_26, 10, 1, 1, 2)
        self.label_5 = QtWidgets.QLabel(Form)
        self.label_5.setObjectName("label_5")
        self.gridLayout.addWidget(self.label_5, 4, 0, 1, 4)
        self.label_6 = QtWidgets.QLabel(Form)
        self.label_6.setObjectName("label_6")
        self.gridLayout.addWidget(self.label_6, 3, 1, 1, 2)
        self.lineEdit_2 = QtWidgets.QLineEdit(Form)
        self.lineEdit_2.setObjectName("lineEdit_2")
        self.gridLayout.addWidget(self.lineEdit_2, 2, 3, 1, 2)
        self.comboBox = QtWidgets.QComboBox(Form)
        self.comboBox.setObjectName("comboBox")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.gridLayout.addWidget(self.comboBox, 18, 0, 1, 3)
        self.label_3 = QtWidgets.QLabel(Form)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 0, 0, 1, 2)
        self.pushButton_2 = QtWidgets.QPushButton(Form)
        self.pushButton_2.setObjectName("pushButton_2")
        self.gridLayout.addWidget(self.pushButton_2, 19, 0, 1, 5)
        self.label_34 = QtWidgets.QLabel(Form)
        self.label_34.setObjectName("label_34")
        self.gridLayout.addWidget(self.label_34, 14, 0, 1, 5)
        self.label_28 = QtWidgets.QLabel(Form)
        self.label_28.setObjectName("label_28")
        self.gridLayout.addWidget(self.label_28, 9, 0, 1, 5)
        self.label_21 = QtWidgets.QLabel(Form)
        self.label_21.setObjectName("label_21")
        self.gridLayout.addWidget(self.label_21, 1, 0, 1, 5)
        self.gridLayout_3.addLayout(self.gridLayout, 0, 0, 1, 1)
        self.gridLayout_2 = QtWidgets.QGridLayout()
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.camera_view_container = QtWidgets.QFrame(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.camera_view_container.sizePolicy().hasHeightForWidth())
        self.camera_view_container.setSizePolicy(sizePolicy)
        self.camera_view_container.setStyleSheet("background-color: rgb(205, 255, 250);")
        self.camera_view_container.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.camera_view_container.setFrameShadow(QtWidgets.QFrame.Raised)
        self.camera_view_container.setObjectName("camera_view_container")
        self.gridLayout_2.addWidget(self.camera_view_container, 0, 0, 1, 3)
        self.pushButton = QtWidgets.QPushButton(Form)
        self.pushButton.setObjectName("pushButton")
        self.gridLayout_2.addWidget(self.pushButton, 1, 2, 1, 1)
        self.label = QtWidgets.QLabel(Form)
        self.label.setObjectName("label")
        self.gridLayout_2.addWidget(self.label, 1, 0, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(428, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_2.addItem(spacerItem, 1, 1, 1, 1)
        self.label_2 = QtWidgets.QLabel(Form)
        self.label_2.setObjectName("label_2")
        self.gridLayout_2.addWidget(self.label_2, 2, 0, 1, 1)
        self.gridLayout_3.addLayout(self.gridLayout_2, 0, 1, 1, 1)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.label_33.setText(_translate("Form", "Time limit"))
        self.label_29.setText(_translate("Form", "Intermediate"))
        self.label_36.setText(_translate("Form", "Feedback to which aspect?"))
        self.label_32.setText(_translate("Form", "Error rate"))
        self.label_7.setText(_translate("Form", "Beginner     "))
        self.label_24.setText(_translate("Form", "Time limit"))
        self.label_25.setText(_translate("Form", "Error rate"))
        self.label_30.setText(_translate("Form", "Time limit"))
        self.label_22.setText(_translate("Form", "Time limit"))
        self.label_27.setText(_translate("Form", "Time limit"))
        self.label_23.setText(_translate("Form", "Error rate"))
        self.label_4.setText(_translate("Form", "Error rate"))
        self.label_31.setText(_translate("Form", "Error rate"))
        self.label_35.setText(_translate("Form", "Competent"))
        self.label_26.setText(_translate("Form", "Error rate"))
        self.label_5.setText(_translate("Form", "Weighted combination:"))
        self.label_6.setText(_translate("Form", "Time limit"))
        self.comboBox.setItemText(0, _translate("Form", "Error rate"))
        self.comboBox.setItemText(1, _translate("Form", "Time limit"))
        self.comboBox.setItemText(2, _translate("Form", "Weighted combination"))
        self.label_3.setText(_translate("Form", "Name exercise:"))
        self.pushButton_2.setText(_translate("Form", "Save"))
        self.label_34.setText(_translate("Form", "Weighted combination:"))
        self.label_28.setText(_translate("Form", "Weighted combination:"))
        self.label_21.setText(_translate("Form", "Target values:"))
        self.pushButton.setText(_translate("Form", "Draw line"))
        self.label.setText(_translate("Form", "Annotation tools: "))
        self.label_2.setText(_translate("Form", "      Instructions \n"
                                                "Line 1...\n"
                                                "Line 2...\n"
                                                "Line3...\n"
                                                "Line 4..."))

#
# if __name__ == "__main__":
#     import sys
#     app = QtWidgets.QApplication(sys.argv)
#     Form = QtWidgets.QWidget()
#     ui = Ui_Form()
#     ui.setupUi(Form)
#     Form.show()
#     sys.exit(app.exec_())
#
