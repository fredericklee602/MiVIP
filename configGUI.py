# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'test.ui'
#
# Created by: PyQt5 UI code generator 5.14.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets
import configparser
# config檔
config = configparser.ConfigParser()
config.read('config.ini')
class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.pushButton_save = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_save.setGeometry(QtCore.QRect(290, 530, 89, 25))
        self.pushButton_save.setObjectName("pushButton_save")
        self.pushButton_cancel = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_cancel.setGeometry(QtCore.QRect(390, 530, 89, 25))
        self.pushButton_cancel.setObjectName("pushButton_cancel")
        self.tableView = QtWidgets.QTableView(self.centralwidget)
        self.tableView.setGeometry(QtCore.QRect(0, 10, 791, 501))
        self.tableView.setObjectName("tableView")
        self.label_apriltag_len = QtWidgets.QLabel(self.centralwidget)
        self.label_apriltag_len.setGeometry(QtCore.QRect(10, 20, 111, 41))
        self.label_apriltag_len.setObjectName("label_apriltag_len")
        self.apriltag_len_Edit = QtWidgets.QLineEdit(self.centralwidget)
        self.apriltag_len_Edit.setGeometry(QtCore.QRect(150, 30, 113, 25))
        self.apriltag_len_Edit.setObjectName("apriltag_len_Edit")
        self.apriltag_fam_Edit = QtWidgets.QLineEdit(self.centralwidget)
        self.apriltag_fam_Edit.setGeometry(QtCore.QRect(150, 70, 113, 25))
        self.apriltag_fam_Edit.setObjectName("apriltag_fam_Edit")
        self.label_apriltag_fam = QtWidgets.QLabel(self.centralwidget)
        self.label_apriltag_fam.setGeometry(QtCore.QRect(10, 60, 111, 41))
        self.label_apriltag_fam.setObjectName("label_apriltag_fam")
        self.label_vaidio_username = QtWidgets.QLabel(self.centralwidget)
        self.label_vaidio_username.setGeometry(QtCore.QRect(10, 160, 121, 41))
        self.label_vaidio_username.setObjectName("label_vaidio_username")
        self.vaidio_username_Edit = QtWidgets.QLineEdit(self.centralwidget)
        self.vaidio_username_Edit.setGeometry(QtCore.QRect(150, 170, 113, 25))
        self.vaidio_username_Edit.setObjectName("vaidio_username_Edit")
        self.vaidio_IP_Edit = QtWidgets.QLineEdit(self.centralwidget)
        self.vaidio_IP_Edit.setGeometry(QtCore.QRect(150, 250, 113, 25))
        self.vaidio_IP_Edit.setObjectName("vaidio_IP_Edit")
        self.label_vaidio_password = QtWidgets.QLabel(self.centralwidget)
        self.label_vaidio_password.setGeometry(QtCore.QRect(10, 200, 121, 41))
        self.label_vaidio_password.setObjectName("label_vaidio_password")
        self.label_vaidio_IP = QtWidgets.QLabel(self.centralwidget)
        self.label_vaidio_IP.setGeometry(QtCore.QRect(10, 240, 121, 41))
        self.label_vaidio_IP.setObjectName("label_vaidio_IP")
        self.vaidio_password_Edit = QtWidgets.QLineEdit(self.centralwidget)
        self.vaidio_password_Edit.setGeometry(QtCore.QRect(150, 210, 113, 25))
        self.vaidio_password_Edit.setObjectName("vaidio_password_Edit")
        self.label_Image_Size = QtWidgets.QLabel(self.centralwidget)
        self.label_Image_Size.setGeometry(QtCore.QRect(10, 330, 121, 41))
        self.label_Image_Size.setObjectName("label_Image_Size")
        self.Image_Size_Edit = QtWidgets.QLineEdit(self.centralwidget)
        self.Image_Size_Edit.setGeometry(QtCore.QRect(150, 340, 113, 25))
        self.Image_Size_Edit.setObjectName("Image_Size_Edit")
        self.label_uav_type = QtWidgets.QLabel(self.centralwidget)
        self.label_uav_type.setGeometry(QtCore.QRect(10, 400, 181, 41))
        self.label_uav_type.setObjectName("label_uav_type")
        self.uav_type_Edit = QtWidgets.QLineEdit(self.centralwidget)
        self.uav_type_Edit.setGeometry(QtCore.QRect(190, 410, 113, 25))
        self.uav_type_Edit.setObjectName("uav_type_Edit")
        self.mysql_host_Edit = QtWidgets.QLineEdit(self.centralwidget)
        self.mysql_host_Edit.setGeometry(QtCore.QRect(560, 30, 113, 25))
        self.mysql_host_Edit.setObjectName("mysql_host_Edit")
        self.label_mysql_host = QtWidgets.QLabel(self.centralwidget)
        self.label_mysql_host.setGeometry(QtCore.QRect(420, 20, 121, 41))
        self.label_mysql_host.setObjectName("label_mysql_host")
        self.mysql_user_Edit = QtWidgets.QLineEdit(self.centralwidget)
        self.mysql_user_Edit.setGeometry(QtCore.QRect(560, 60, 113, 25))
        self.mysql_user_Edit.setObjectName("mysql_user_Edit")
        self.label_mysql_user = QtWidgets.QLabel(self.centralwidget)
        self.label_mysql_user.setGeometry(QtCore.QRect(420, 50, 121, 41))
        self.label_mysql_user.setObjectName("label_mysql_user")
        self.label_mysql_password = QtWidgets.QLabel(self.centralwidget)
        self.label_mysql_password.setGeometry(QtCore.QRect(420, 80, 121, 41))
        self.label_mysql_password.setObjectName("label_mysql_password")
        self.mysql_password_Edit = QtWidgets.QLineEdit(self.centralwidget)
        self.mysql_password_Edit.setGeometry(QtCore.QRect(560, 90, 113, 25))
        self.mysql_password_Edit.setObjectName("mysql_password_Edit")
        self.mysql_database_Edit = QtWidgets.QLineEdit(self.centralwidget)
        self.mysql_database_Edit.setGeometry(QtCore.QRect(560, 120, 113, 25))
        self.mysql_database_Edit.setObjectName("mysql_database_Edit")
        self.label_mysql_database = QtWidgets.QLabel(self.centralwidget)
        self.label_mysql_database.setGeometry(QtCore.QRect(420, 110, 121, 41))
        self.label_mysql_database.setObjectName("label_mysql_database")
        self.label_sift_threshold = QtWidgets.QLabel(self.centralwidget)
        self.label_sift_threshold.setGeometry(QtCore.QRect(420, 330, 121, 41))
        self.label_sift_threshold.setObjectName("label_sift_threshold")
        self.vaidio_sift_threshold = QtWidgets.QLineEdit(self.centralwidget)
        self.vaidio_sift_threshold.setGeometry(QtCore.QRect(560, 340, 113, 25))
        self.vaidio_sift_threshold.setObjectName("vaidio_sift_threshold")
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.pushButton_save.setText(_translate("MainWindow", "save"))
        self.pushButton_cancel.setText(_translate("MainWindow", "close"))
        self.label_apriltag_len.setText(_translate("MainWindow", "Apriltag Length"))
        self.apriltag_len_Edit.setText(_translate("MainWindow", config['apriltag']["pic_length"]))
        self.apriltag_fam_Edit.setText(_translate("MainWindow", config['apriltag']["family"]))
        self.label_apriltag_fam.setText(_translate("MainWindow", "Apriltag Family"))
        self.label_vaidio_username.setText(_translate("MainWindow", "Vaidio username"))
        self.vaidio_username_Edit.setText(_translate("MainWindow", config['vaidio']["username"]))
        self.vaidio_IP_Edit.setText(_translate("MainWindow", config['vaidio']["ip"]))
        self.label_vaidio_password.setText(_translate("MainWindow", "Vaidio password"))
        self.label_vaidio_IP.setText(_translate("MainWindow", "Vaidio IP"))
        self.vaidio_password_Edit.setText(_translate("MainWindow", config['vaidio']["password"]))
        self.label_Image_Size.setText(_translate("MainWindow", "Image Size"))
        self.Image_Size_Edit.setText(_translate("MainWindow", config['img_size']["640"]))
        self.label_uav_type.setText(_translate("MainWindow", "UAV type (deck or seeker)"))
        self.uav_type_Edit.setText(_translate("MainWindow", config['UAV_type']["UAV_name"]))
        self.mysql_host_Edit.setText(_translate("MainWindow", config['MYSQL']["host"]))
        self.label_mysql_host.setText(_translate("MainWindow", "MYSQL host"))
        self.mysql_user_Edit.setText(_translate("MainWindow", config['MYSQL']["user"]))
        self.label_mysql_user.setText(_translate("MainWindow", "MYSQL user"))
        self.label_mysql_password.setText(_translate("MainWindow", "MYSQL password"))
        self.mysql_password_Edit.setText(_translate("MainWindow", config['MYSQL']["password"]))
        self.mysql_database_Edit.setText(_translate("MainWindow", config['MYSQL']["database"]))
        self.label_mysql_database.setText(_translate("MainWindow", "MYSQL database"))
        self.label_sift_threshold.setText(_translate("MainWindow", "SIFT threshold"))
        self.vaidio_sift_threshold.setText(_translate("MainWindow", config['SIFT']["match_threshold"]))


        self.pushButton_save.clicked.connect(self.clickMethod)
        self.pushButton_cancel.clicked.connect(QtWidgets.QApplication.instance().quit)
    def clickMethod(self):
        config_ = config
        config_['apriltag']["pic_length"] = self.apriltag_len_Edit.text()
        config_['apriltag']["family"] = self.apriltag_fam_Edit.text()
        config_['vaidio']["username"] = self.vaidio_username_Edit.text()
        config_['vaidio']["ip"] = self.vaidio_IP_Edit.text()
        config_['vaidio']["password"] = self.vaidio_password_Edit.text()
        config_['img_size']["640"] = self.Image_Size_Edit.text()
        config_['UAV_type']["UAV_name"] = self.uav_type_Edit.text()
        config_['MYSQL']["host"] = self.mysql_host_Edit.text()
        config_['MYSQL']["user"] = self.mysql_user_Edit.text()
        config_['MYSQL']["password"] = self.mysql_password_Edit.text()
        config_['MYSQL']["database"] = self.mysql_database_Edit.text()
        config_['SIFT']["match_threshold"] = self.vaidio_sift_threshold.text()
        with open('config.ini', 'w') as configfile:
            config_.write(configfile)
class ExecuteGUI:
    def exec(self):
        import sys
        app = QtWidgets.QApplication(sys.argv)
        MainWindow = QtWidgets.QMainWindow()
        ui = Ui_MainWindow()
        ui.setupUi(MainWindow)
        MainWindow.show()
        app.exec_()
        # sys.exit(app.exec_())