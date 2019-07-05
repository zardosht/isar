# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'scene_definition.ui'
#
# Created by: PyQt5 UI code generator 5.12.3
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_SceneDefinitionWindow(object):
    def setupUi(self, SceneDefinitionWindow):
        SceneDefinitionWindow.setObjectName("SceneDefinitionWindow")
        SceneDefinitionWindow.resize(1543, 939)
        self.centralWidget = QtWidgets.QWidget(SceneDefinitionWindow)
        self.centralWidget.setObjectName("centralWidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.centralWidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setSpacing(6)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.frame_1 = QtWidgets.QFrame(self.centralWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(10)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame_1.sizePolicy().hasHeightForWidth())
        self.frame_1.setSizePolicy(sizePolicy)
        self.frame_1.setMaximumSize(QtCore.QSize(200, 16777215))
        self.frame_1.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_1.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_1.setObjectName("frame_1")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.frame_1)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.label_2 = QtWidgets.QLabel(self.frame_1)
        self.label_2.setObjectName("label_2")
        self.verticalLayout_2.addWidget(self.label_2)
        self.scenes_list = QtWidgets.QListView(self.frame_1)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(10)
        sizePolicy.setHeightForWidth(self.scenes_list.sizePolicy().hasHeightForWidth())
        self.scenes_list.setSizePolicy(sizePolicy)
        self.scenes_list.setObjectName("scenes_list")
        self.verticalLayout_2.addWidget(self.scenes_list)
        self.frame = QtWidgets.QFrame(self.frame_1)
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout(self.frame)
        self.horizontalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_5.setSpacing(6)
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_5.addItem(spacerItem)
        self.scene_up_btn = QtWidgets.QToolButton(self.frame)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("images/up_button.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.scene_up_btn.setIcon(icon)
        self.scene_up_btn.setObjectName("scene_up_btn")
        self.horizontalLayout_5.addWidget(self.scene_up_btn)
        self.scene_down_btn = QtWidgets.QToolButton(self.frame)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap("images/down_button.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.scene_down_btn.setIcon(icon1)
        self.scene_down_btn.setObjectName("scene_down_btn")
        self.horizontalLayout_5.addWidget(self.scene_down_btn)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_5.addItem(spacerItem1)
        self.verticalLayout_2.addWidget(self.frame)
        self.new_scene_btn = QtWidgets.QPushButton(self.frame_1)
        self.new_scene_btn.setObjectName("new_scene_btn")
        self.verticalLayout_2.addWidget(self.new_scene_btn)
        self.clone_scene_btn = QtWidgets.QPushButton(self.frame_1)
        self.clone_scene_btn.setObjectName("clone_scene_btn")
        self.verticalLayout_2.addWidget(self.clone_scene_btn)
        self.delete_scene_btn = QtWidgets.QPushButton(self.frame_1)
        self.delete_scene_btn.setObjectName("delete_scene_btn")
        self.verticalLayout_2.addWidget(self.delete_scene_btn)
        self.init_scene_size_btn = QtWidgets.QPushButton(self.frame_1)
        self.init_scene_size_btn.setObjectName("init_scene_size_btn")
        self.verticalLayout_2.addWidget(self.init_scene_size_btn)
        self.define_navigation_flow_btn = QtWidgets.QPushButton(self.frame_1)
        self.define_navigation_flow_btn.setObjectName("define_navigation_flow_btn")
        self.verticalLayout_2.addWidget(self.define_navigation_flow_btn)
        self.ev_act_rules_btn = QtWidgets.QPushButton(self.frame_1)
        self.ev_act_rules_btn.setObjectName("ev_act_rules_btn")
        self.verticalLayout_2.addWidget(self.ev_act_rules_btn)
        self.line = QtWidgets.QFrame(self.frame_1)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.line.sizePolicy().hasHeightForWidth())
        self.line.setSizePolicy(sizePolicy)
        self.line.setMinimumSize(QtCore.QSize(0, 20))
        self.line.setLineWidth(10)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.verticalLayout_2.addWidget(self.line)
        self.project_name_le = QtWidgets.QLineEdit(self.frame_1)
        self.project_name_le.setObjectName("project_name_le")
        self.verticalLayout_2.addWidget(self.project_name_le)
        self.create_proj_btn = QtWidgets.QPushButton(self.frame_1)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.create_proj_btn.setFont(font)
        self.create_proj_btn.setObjectName("create_proj_btn")
        self.verticalLayout_2.addWidget(self.create_proj_btn)
        self.save_proj_btn = QtWidgets.QPushButton(self.frame_1)
        self.save_proj_btn.setObjectName("save_proj_btn")
        self.verticalLayout_2.addWidget(self.save_proj_btn)
        self.load_proj_btn = QtWidgets.QPushButton(self.frame_1)
        self.load_proj_btn.setObjectName("load_proj_btn")
        self.verticalLayout_2.addWidget(self.load_proj_btn)
        self.horizontalLayout.addWidget(self.frame_1)
        self.frame_2 = QtWidgets.QFrame(self.centralWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(90)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame_2.sizePolicy().hasHeightForWidth())
        self.frame_2.setSizePolicy(sizePolicy)
        self.frame_2.setMinimumSize(QtCore.QSize(800, 0))
        self.frame_2.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_2.setObjectName("frame_2")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.frame_2)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.frame_3 = QtWidgets.QFrame(self.frame_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(5)
        sizePolicy.setHeightForWidth(self.frame_3.sizePolicy().hasHeightForWidth())
        self.frame_3.setSizePolicy(sizePolicy)
        self.frame_3.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_3.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_3.setObjectName("frame_3")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.frame_3)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setSpacing(6)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.camers_view_frame = QtWidgets.QFrame(self.frame_3)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(60)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.camers_view_frame.sizePolicy().hasHeightForWidth())
        self.camers_view_frame.setSizePolicy(sizePolicy)
        self.camers_view_frame.setMinimumSize(QtCore.QSize(250, 250))
        self.camers_view_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.camers_view_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.camers_view_frame.setObjectName("camers_view_frame")
        self.verticalLayout_6 = QtWidgets.QVBoxLayout(self.camers_view_frame)
        self.verticalLayout_6.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_6.setSpacing(6)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.camera_view_container = QtWidgets.QFrame(self.camers_view_frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.camera_view_container.sizePolicy().hasHeightForWidth())
        self.camera_view_container.setSizePolicy(sizePolicy)
        self.camera_view_container.setStyleSheet("background-color: rgb(205, 255, 250);")
        self.camera_view_container.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.camera_view_container.setFrameShadow(QtWidgets.QFrame.Raised)
        self.camera_view_container.setObjectName("camera_view_container")
        self.verticalLayout_6.addWidget(self.camera_view_container)
        self.camera_view_toolbox = QtWidgets.QFrame(self.camers_view_frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.camera_view_toolbox.sizePolicy().hasHeightForWidth())
        self.camera_view_toolbox.setSizePolicy(sizePolicy)
        self.camera_view_toolbox.setMaximumSize(QtCore.QSize(16777215, 40))
        self.camera_view_toolbox.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.camera_view_toolbox.setFrameShadow(QtWidgets.QFrame.Raised)
        self.camera_view_toolbox.setObjectName("camera_view_toolbox")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.camera_view_toolbox)
        self.horizontalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_4.setSpacing(6)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.select_btn = QtWidgets.QToolButton(self.camera_view_toolbox)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap("images/select.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.select_btn.setIcon(icon2)
        self.select_btn.setCheckable(True)
        self.select_btn.setAutoExclusive(False)
        self.select_btn.setObjectName("select_btn")
        self.annotation_buttons = QtWidgets.QButtonGroup(SceneDefinitionWindow)
        self.annotation_buttons.setObjectName("annotation_buttons")
        self.annotation_buttons.addButton(self.select_btn)
        self.horizontalLayout_4.addWidget(self.select_btn)
        self.delete_btn = QtWidgets.QToolButton(self.camera_view_toolbox)
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap("images/delete.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.delete_btn.setIcon(icon3)
        self.delete_btn.setObjectName("delete_btn")
        self.horizontalLayout_4.addWidget(self.delete_btn)
        self.undo_btn = QtWidgets.QToolButton(self.camera_view_toolbox)
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap("images/undo.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.undo_btn.setIcon(icon4)
        self.undo_btn.setObjectName("undo_btn")
        self.horizontalLayout_4.addWidget(self.undo_btn)
        self.redo_btn = QtWidgets.QToolButton(self.camera_view_toolbox)
        icon5 = QtGui.QIcon()
        icon5.addPixmap(QtGui.QPixmap("images/redo.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.redo_btn.setIcon(icon5)
        self.redo_btn.setObjectName("redo_btn")
        self.horizontalLayout_4.addWidget(self.redo_btn)
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem2)
        self.mouse_object_position_label = QtWidgets.QLabel(self.camera_view_toolbox)
        self.mouse_object_position_label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.mouse_object_position_label.setObjectName("mouse_object_position_label")
        self.horizontalLayout_4.addWidget(self.mouse_object_position_label)
        self.mouse_image_position_label = QtWidgets.QLabel(self.camera_view_toolbox)
        self.mouse_image_position_label.setMinimumSize(QtCore.QSize(100, 0))
        self.mouse_image_position_label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.mouse_image_position_label.setObjectName("mouse_image_position_label")
        self.horizontalLayout_4.addWidget(self.mouse_image_position_label)
        self.verticalLayout_6.addWidget(self.camera_view_toolbox)
        self.horizontalLayout_2.addWidget(self.camers_view_frame)
        self.splitter = QtWidgets.QSplitter(self.frame_3)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(40)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.splitter.sizePolicy().hasHeightForWidth())
        self.splitter.setSizePolicy(sizePolicy)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setHandleWidth(5)
        self.splitter.setChildrenCollapsible(False)
        self.splitter.setObjectName("splitter")
        self.objects_view_frame = QtWidgets.QFrame(self.splitter)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(30)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.objects_view_frame.sizePolicy().hasHeightForWidth())
        self.objects_view_frame.setSizePolicy(sizePolicy)
        self.objects_view_frame.setMaximumSize(QtCore.QSize(200, 16777215))
        self.objects_view_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.objects_view_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.objects_view_frame.setObjectName("objects_view_frame")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.objects_view_frame)
        self.verticalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_4.setSpacing(6)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.label_3 = QtWidgets.QLabel(self.objects_view_frame)
        self.label_3.setObjectName("label_3")
        self.verticalLayout_4.addWidget(self.label_3)
        self.track_objects_checkbox = QtWidgets.QCheckBox(self.objects_view_frame)
        self.track_objects_checkbox.setObjectName("track_objects_checkbox")
        self.verticalLayout_4.addWidget(self.track_objects_checkbox)
        self.label_5 = QtWidgets.QLabel(self.objects_view_frame)
        self.label_5.setObjectName("label_5")
        self.verticalLayout_4.addWidget(self.label_5)
        self.annotations_list = QtWidgets.QListView(self.objects_view_frame)
        self.annotations_list.setObjectName("annotations_list")
        self.verticalLayout_4.addWidget(self.annotations_list)
        self.properties_view_frame = QtWidgets.QFrame(self.splitter)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(70)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.properties_view_frame.sizePolicy().hasHeightForWidth())
        self.properties_view_frame.setSizePolicy(sizePolicy)
        self.properties_view_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.properties_view_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.properties_view_frame.setObjectName("properties_view_frame")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.properties_view_frame)
        self.verticalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_5.setSpacing(6)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.label_4 = QtWidgets.QLabel(self.properties_view_frame)
        self.label_4.setObjectName("label_4")
        self.verticalLayout_5.addWidget(self.label_4)
        self.properties_view = QtWidgets.QTableView(self.properties_view_frame)
        self.properties_view.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.properties_view.setObjectName("properties_view")
        self.properties_view.horizontalHeader().setMinimumSectionSize(5)
        self.properties_view.verticalHeader().setMinimumSectionSize(5)
        self.verticalLayout_5.addWidget(self.properties_view)
        self.horizontalLayout_2.addWidget(self.splitter)
        self.verticalLayout.addWidget(self.frame_3)
        self.annotations_frame = QtWidgets.QFrame(self.frame_2)
        self.annotations_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.annotations_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.annotations_frame.setObjectName("annotations_frame")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.annotations_frame)
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_3.setSpacing(0)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.label = QtWidgets.QLabel(self.annotations_frame)
        self.label.setObjectName("label")
        self.verticalLayout_3.addWidget(self.label)
        self.frame_4 = QtWidgets.QFrame(self.annotations_frame)
        self.frame_4.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_4.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_4.setObjectName("frame_4")
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout(self.frame_4)
        self.horizontalLayout_6.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_6.setSpacing(0)
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setSpacing(6)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.text_btn = QtWidgets.QToolButton(self.frame_4)
        icon6 = QtGui.QIcon()
        icon6.addPixmap(QtGui.QPixmap("images/text.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.text_btn.setIcon(icon6)
        self.text_btn.setCheckable(True)
        self.text_btn.setAutoExclusive(True)
        self.text_btn.setAutoRaise(False)
        self.text_btn.setObjectName("text_btn")
        self.annotation_buttons.addButton(self.text_btn)
        self.horizontalLayout_3.addWidget(self.text_btn)
        self.audio_btn = QtWidgets.QToolButton(self.frame_4)
        icon7 = QtGui.QIcon()
        icon7.addPixmap(QtGui.QPixmap("images/audio.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.audio_btn.setIcon(icon7)
        self.audio_btn.setCheckable(True)
        self.audio_btn.setAutoExclusive(True)
        self.audio_btn.setObjectName("audio_btn")
        self.annotation_buttons.addButton(self.audio_btn)
        self.horizontalLayout_3.addWidget(self.audio_btn)
        self.arrow_btn = QtWidgets.QToolButton(self.frame_4)
        icon8 = QtGui.QIcon()
        icon8.addPixmap(QtGui.QPixmap("images/arrow.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.arrow_btn.setIcon(icon8)
        self.arrow_btn.setCheckable(True)
        self.arrow_btn.setAutoExclusive(True)
        self.arrow_btn.setObjectName("arrow_btn")
        self.annotation_buttons.addButton(self.arrow_btn)
        self.horizontalLayout_3.addWidget(self.arrow_btn)
        self.check_box_btn = QtWidgets.QToolButton(self.frame_4)
        icon9 = QtGui.QIcon()
        icon9.addPixmap(QtGui.QPixmap("images/check_box.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.check_box_btn.setIcon(icon9)
        self.check_box_btn.setCheckable(True)
        self.check_box_btn.setAutoExclusive(True)
        self.check_box_btn.setObjectName("check_box_btn")
        self.annotation_buttons.addButton(self.check_box_btn)
        self.horizontalLayout_3.addWidget(self.check_box_btn)
        self.video_btn = QtWidgets.QToolButton(self.frame_4)
        icon10 = QtGui.QIcon()
        icon10.addPixmap(QtGui.QPixmap("images/video.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.video_btn.setIcon(icon10)
        self.video_btn.setCheckable(True)
        self.video_btn.setAutoExclusive(True)
        self.video_btn.setObjectName("video_btn")
        self.annotation_buttons.addButton(self.video_btn)
        self.horizontalLayout_3.addWidget(self.video_btn)
        self.relationship_btn = QtWidgets.QToolButton(self.frame_4)
        icon11 = QtGui.QIcon()
        icon11.addPixmap(QtGui.QPixmap("images/relationship.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.relationship_btn.setIcon(icon11)
        self.relationship_btn.setCheckable(True)
        self.relationship_btn.setAutoExclusive(True)
        self.relationship_btn.setObjectName("relationship_btn")
        self.annotation_buttons.addButton(self.relationship_btn)
        self.horizontalLayout_3.addWidget(self.relationship_btn)
        self.timer_btn = QtWidgets.QToolButton(self.frame_4)
        icon12 = QtGui.QIcon()
        icon12.addPixmap(QtGui.QPixmap("images/timer.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.timer_btn.setIcon(icon12)
        self.timer_btn.setCheckable(True)
        self.timer_btn.setAutoExclusive(True)
        self.timer_btn.setObjectName("timer_btn")
        self.annotation_buttons.addButton(self.timer_btn)
        self.horizontalLayout_3.addWidget(self.timer_btn)
        self.image_btn = QtWidgets.QToolButton(self.frame_4)
        icon13 = QtGui.QIcon()
        icon13.addPixmap(QtGui.QPixmap("images/image.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.image_btn.setIcon(icon13)
        self.image_btn.setCheckable(True)
        self.image_btn.setAutoExclusive(True)
        self.image_btn.setObjectName("image_btn")
        self.annotation_buttons.addButton(self.image_btn)
        self.horizontalLayout_3.addWidget(self.image_btn)
        self.rectangle_btn = QtWidgets.QToolButton(self.frame_4)
        icon14 = QtGui.QIcon()
        icon14.addPixmap(QtGui.QPixmap("images/rectangle.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.rectangle_btn.setIcon(icon14)
        self.rectangle_btn.setCheckable(True)
        self.rectangle_btn.setAutoExclusive(True)
        self.rectangle_btn.setObjectName("rectangle_btn")
        self.annotation_buttons.addButton(self.rectangle_btn)
        self.horizontalLayout_3.addWidget(self.rectangle_btn)
        self.line_btn = QtWidgets.QToolButton(self.frame_4)
        icon15 = QtGui.QIcon()
        icon15.addPixmap(QtGui.QPixmap("images/line.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.line_btn.setIcon(icon15)
        self.line_btn.setCheckable(True)
        self.line_btn.setAutoExclusive(True)
        self.line_btn.setObjectName("line_btn")
        self.annotation_buttons.addButton(self.line_btn)
        self.horizontalLayout_3.addWidget(self.line_btn)
        self.circle_btn = QtWidgets.QToolButton(self.frame_4)
        icon16 = QtGui.QIcon()
        icon16.addPixmap(QtGui.QPixmap("images/circle.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.circle_btn.setIcon(icon16)
        self.circle_btn.setCheckable(True)
        self.circle_btn.setAutoExclusive(True)
        self.circle_btn.setObjectName("circle_btn")
        self.annotation_buttons.addButton(self.circle_btn)
        self.horizontalLayout_3.addWidget(self.circle_btn)
        self.action_button_btn = QtWidgets.QToolButton(self.frame_4)
        icon17 = QtGui.QIcon()
        icon17.addPixmap(QtGui.QPixmap("images/action_button.jpg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.action_button_btn.setIcon(icon17)
        self.action_button_btn.setCheckable(True)
        self.action_button_btn.setAutoExclusive(True)
        self.action_button_btn.setObjectName("action_button_btn")
        self.annotation_buttons.addButton(self.action_button_btn)
        self.horizontalLayout_3.addWidget(self.action_button_btn)
        self.curve_btn = QtWidgets.QToolButton(self.frame_4)
        icon18 = QtGui.QIcon()
        icon18.addPixmap(QtGui.QPixmap("images/curve_line.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.curve_btn.setIcon(icon18)
        self.curve_btn.setCheckable(True)
        self.curve_btn.setAutoExclusive(True)
        self.curve_btn.setObjectName("curve_btn")
        self.annotation_buttons.addButton(self.curve_btn)
        self.horizontalLayout_3.addWidget(self.curve_btn)
        self.animation_btn = QtWidgets.QToolButton(self.frame_4)
        icon19 = QtGui.QIcon()
        icon19.addPixmap(QtGui.QPixmap("images/animation.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.animation_btn.setIcon(icon19)
        self.animation_btn.setCheckable(True)
        self.animation_btn.setAutoExclusive(True)
        self.animation_btn.setObjectName("animation_btn")
        self.annotation_buttons.addButton(self.animation_btn)
        self.horizontalLayout_3.addWidget(self.animation_btn)
        self.feedback_btn = QtWidgets.QToolButton(self.frame_4)
        icon20 = QtGui.QIcon()
        icon20.addPixmap(QtGui.QPixmap("images/feedback.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.feedback_btn.setIcon(icon20)
        self.feedback_btn.setCheckable(True)
        self.feedback_btn.setAutoExclusive(True)
        self.feedback_btn.setObjectName("feedback_btn")
        self.annotation_buttons.addButton(self.feedback_btn)
        self.horizontalLayout_3.addWidget(self.feedback_btn)
        self.object_area_btn = QtWidgets.QToolButton(self.frame_4)
        icon21 = QtGui.QIcon()
        icon21.addPixmap(QtGui.QPixmap("images/object_area.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.object_area_btn.setIcon(icon21)
        self.object_area_btn.setCheckable(True)
        self.object_area_btn.setAutoExclusive(True)
        self.object_area_btn.setObjectName("object_area_btn")
        self.annotation_buttons.addButton(self.object_area_btn)
        self.horizontalLayout_3.addWidget(self.object_area_btn)
        spacerItem3 = QtWidgets.QSpacerItem(638, 17, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem3)
        self.horizontalLayout_6.addLayout(self.horizontalLayout_3)
        self.verticalLayout_3.addWidget(self.frame_4)
        self.verticalLayout.addWidget(self.annotations_frame)
        self.horizontalLayout.addWidget(self.frame_2)
        SceneDefinitionWindow.setCentralWidget(self.centralWidget)
        self.menuBar = QtWidgets.QMenuBar(SceneDefinitionWindow)
        self.menuBar.setGeometry(QtCore.QRect(0, 0, 1543, 22))
        self.menuBar.setObjectName("menuBar")
        self.menuFile = QtWidgets.QMenu(self.menuBar)
        self.menuFile.setObjectName("menuFile")
        SceneDefinitionWindow.setMenuBar(self.menuBar)
        self.mainToolBar = QtWidgets.QToolBar(SceneDefinitionWindow)
        self.mainToolBar.setObjectName("mainToolBar")
        SceneDefinitionWindow.addToolBar(QtCore.Qt.TopToolBarArea, self.mainToolBar)
        self.statusBar = QtWidgets.QStatusBar(SceneDefinitionWindow)
        self.statusBar.setObjectName("statusBar")
        SceneDefinitionWindow.setStatusBar(self.statusBar)
        self.actionCreate_Project = QtWidgets.QAction(SceneDefinitionWindow)
        self.actionCreate_Project.setObjectName("actionCreate_Project")
        self.actionLoad_Project = QtWidgets.QAction(SceneDefinitionWindow)
        self.actionLoad_Project.setObjectName("actionLoad_Project")
        self.actionSave_Project = QtWidgets.QAction(SceneDefinitionWindow)
        self.actionSave_Project.setObjectName("actionSave_Project")
        self.actionEvents = QtWidgets.QAction(SceneDefinitionWindow)
        self.actionEvents.setObjectName("actionEvents")
        self.actionActions = QtWidgets.QAction(SceneDefinitionWindow)
        self.actionActions.setObjectName("actionActions")
        self.actionRules = QtWidgets.QAction(SceneDefinitionWindow)
        self.actionRules.setObjectName("actionRules")
        self.menuFile.addAction(self.actionLoad_Project)
        self.menuBar.addAction(self.menuFile.menuAction())

        self.retranslateUi(SceneDefinitionWindow)
        QtCore.QMetaObject.connectSlotsByName(SceneDefinitionWindow)

    def retranslateUi(self, SceneDefinitionWindow):
        _translate = QtCore.QCoreApplication.translate
        SceneDefinitionWindow.setWindowTitle(_translate("SceneDefinitionWindow", "SceneDefinitionWindow"))
        self.label_2.setText(_translate("SceneDefinitionWindow", "Scenes"))
        self.scene_up_btn.setText(_translate("SceneDefinitionWindow", "..."))
        self.scene_down_btn.setText(_translate("SceneDefinitionWindow", "..."))
        self.new_scene_btn.setText(_translate("SceneDefinitionWindow", "New Scene"))
        self.clone_scene_btn.setText(_translate("SceneDefinitionWindow", "Clone"))
        self.delete_scene_btn.setText(_translate("SceneDefinitionWindow", "Delete"))
        self.init_scene_size_btn.setText(_translate("SceneDefinitionWindow", "Init Scn Size"))
        self.define_navigation_flow_btn.setText(_translate("SceneDefinitionWindow", "Nav. Flow ..."))
        self.ev_act_rules_btn.setText(_translate("SceneDefinitionWindow", "Ev., Act., Rules ..."))
        self.project_name_le.setText(_translate("SceneDefinitionWindow", "[project_name]"))
        self.create_proj_btn.setText(_translate("SceneDefinitionWindow", "CreateProject..."))
        self.save_proj_btn.setText(_translate("SceneDefinitionWindow", "Save..."))
        self.load_proj_btn.setText(_translate("SceneDefinitionWindow", "Load..."))
        self.select_btn.setText(_translate("SceneDefinitionWindow", "..."))
        self.delete_btn.setText(_translate("SceneDefinitionWindow", "..."))
        self.undo_btn.setText(_translate("SceneDefinitionWindow", "..."))
        self.redo_btn.setText(_translate("SceneDefinitionWindow", "..."))
        self.mouse_object_position_label.setText(_translate("SceneDefinitionWindow", "mouse object position"))
        self.mouse_image_position_label.setText(_translate("SceneDefinitionWindow", "mouse image position"))
        self.label_3.setText(_translate("SceneDefinitionWindow", "Physical Objects"))
        self.track_objects_checkbox.setText(_translate("SceneDefinitionWindow", "Track Objects"))
        self.label_5.setText(_translate("SceneDefinitionWindow", "Annotations"))
        self.label_4.setText(_translate("SceneDefinitionWindow", "Properties"))
        self.label.setText(_translate("SceneDefinitionWindow", "Annotation Tools"))
        self.text_btn.setText(_translate("SceneDefinitionWindow", "..."))
        self.arrow_btn.setText(_translate("SceneDefinitionWindow", "..."))
        self.check_box_btn.setText(_translate("SceneDefinitionWindow", "..."))
        self.video_btn.setText(_translate("SceneDefinitionWindow", "..."))
        self.relationship_btn.setText(_translate("SceneDefinitionWindow", "..."))
        self.timer_btn.setText(_translate("SceneDefinitionWindow", "..."))
        self.image_btn.setText(_translate("SceneDefinitionWindow", "..."))
        self.rectangle_btn.setText(_translate("SceneDefinitionWindow", "..."))
        self.line_btn.setText(_translate("SceneDefinitionWindow", "..."))
        self.circle_btn.setText(_translate("SceneDefinitionWindow", "..."))
        self.action_button_btn.setText(_translate("SceneDefinitionWindow", "..."))
        self.curve_btn.setText(_translate("SceneDefinitionWindow", "..."))
        self.animation_btn.setText(_translate("SceneDefinitionWindow", "..."))
        self.feedback_btn.setText(_translate("SceneDefinitionWindow", "..."))
        self.object_area_btn.setText(_translate("SceneDefinitionWindow", "..."))
        self.menuFile.setTitle(_translate("SceneDefinitionWindow", "File"))
        self.actionCreate_Project.setText(_translate("SceneDefinitionWindow", "Create Project ..."))
        self.actionLoad_Project.setText(_translate("SceneDefinitionWindow", "Load Project ..."))
        self.actionSave_Project.setText(_translate("SceneDefinitionWindow", "Save Project ..."))
        self.actionEvents.setText(_translate("SceneDefinitionWindow", "Events ..."))
        self.actionActions.setText(_translate("SceneDefinitionWindow", "Actions ..."))
        self.actionRules.setText(_translate("SceneDefinitionWindow", "Rules ..."))
