from Vaidio_API import API
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QWidget, QApplication, QLabel, QVBoxLayout
from PyQt5.QtGui import QPixmap
import sys
import cv2
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt, QThread
import numpy as np
import configparser
# config檔
config = configparser.ConfigParser()
config.read('config.ini')
class Cal_Calibrate(QThread):
    def run(self,objpoints, imgpoints):
        ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, (640, 480), None, None)
        print("mtx\n" + str(mtx))
        print("dist\n" + str(dist))
        print("已經完成相機內參計算")
        text = "mtx\n" + str(mtx) + "\ndist\n" + str(dist) + "\n已經完成相機內參計算"
        return text, mtx, dist

class VideoThread(QThread):
    change_pixmap_signal = pyqtSignal(np.ndarray)
    change_text_signal = pyqtSignal(str)
    def __init__(self,cameraID,chess_width,data_length):
        super().__init__()
        self._run_flag = True
        self.data_length = data_length
        self.calibrate_ready = False
        self.cal_Calibrate = Cal_Calibrate()
        self.api = API()
        self.cameraID = cameraID
        self.chess_width = chess_width
        self.mtx = np.array([])
        self.dist = np.array([])
    def run(self):
        # capture from web cam
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
        Nx_cor = 9
        Ny_cor = 6

        objp = np.zeros((Nx_cor * Ny_cor, 3), np.float32)
        objp[:, :2] = np.mgrid[0:Nx_cor, 0:Ny_cor].T.reshape(-1, 2)
        objp = objp*self.chess_width
        objpoints = []  # 3d points in real world space
        imgpoints = []  # 2d points in image plane.
        # cap = cv2.VideoCapture(0)
        count = 0
        data_count = 0
        while self._run_flag:
            count += 1
            # ret, cv_img = cap.read()
            cv_img, gray = self.api.GetStreamImage(self.cameraID)
            if cv_img.sum()>0:
                gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
                gray = cv2.resize(gray,(640,480))
                ret_, corners = cv2.findChessboardCorners(gray, (Nx_cor, Ny_cor), None)  # Find the corners
                if ret_ == True and data_count<self.data_length:
                    corners = cv2.cornerSubPix(gray, corners, (7, 7), (-1, -1), criteria)
                    objpoints.append(objp)
                    imgpoints.append(corners)
                    # cv2.imwrite('./chess/frame'+str(count)+".jpg", cv_img)
                    cv2.drawChessboardCorners(cv_img, (Nx_cor, Ny_cor), corners, ret_)
                    if count%5 == 0:
                        data_count+=1
                        if data_count%10 == 0:
                            text = "完成10筆corners data"
                            self.change_text_signal.emit(text)
                try:
                    self.change_pixmap_signal.emit(cv_img)
                except:
                    return
                if data_count==self.data_length and self.calibrate_ready == False:
                    text = "已經完成{0}筆corners data".format(self.data_length)
                    self.change_text_signal.emit(text)
                    text = "正在計算相機內參請稍待"
                    self.change_text_signal.emit(text)
                    text, self.mtx, self.dist = self.cal_Calibrate.run(objpoints,imgpoints)
                    self.change_text_signal.emit(text)
                    self.calibrate_ready = True
                
        # shut down capture system
        # cap.release()

    def stop(self):
        """Sets run flag to False and waits for thread to finish"""
        self._run_flag = False
        self.wait()
class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(875, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(260, 50, 441, 61))
        self.label.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.scrollArea = QtWidgets.QScrollArea(self.centralwidget)
        self.scrollArea.setGeometry(QtCore.QRect(730, 140, 131, 370))
        self.scrollArea.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 129, 409))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.formLayout = QtWidgets.QFormLayout()
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.img_label = QtWidgets.QLabel(self.centralwidget)
        self.img_label.setGeometry(QtCore.QRect(260, 140, 431, 371))
        self.img_label.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.img_label.setLineWidth(6)
        self.img_label.setText("")
        self.img_label.setObjectName("img_label")
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(30, 140, 150, 25))
        self.pushButton.setObjectName("pushButton")
        self.label_cameraID = QtWidgets.QLabel(self.centralwidget)
        self.label_cameraID.setGeometry(QtCore.QRect(30, 180, 150, 25))
        self.label_cameraID.setObjectName("label_cameraID")
        self.cameraID_Edit = QtWidgets.QLineEdit(self.centralwidget)
        self.cameraID_Edit.setGeometry(QtCore.QRect(30, 220, 150, 25))
        self.cameraID_Edit.setObjectName("cameraID_Edit")
        self.label_chess_width = QtWidgets.QLabel(self.centralwidget)
        self.label_chess_width.setGeometry(QtCore.QRect(30, 280, 150, 25))
        self.label_chess_width.setObjectName("label_chess_width")
        self.chess_width_Edit = QtWidgets.QLineEdit(self.centralwidget)
        self.chess_width_Edit.setGeometry(QtCore.QRect(30, 320, 150, 25))
        self.chess_width_Edit.setObjectName("chess_width_Edit")
        self.label_data_length = QtWidgets.QLabel(self.centralwidget)
        self.label_data_length.setGeometry(QtCore.QRect(30, 360, 150, 25))
        self.label_data_length.setObjectName("label_chess_width")
        self.data_length_Edit = QtWidgets.QLineEdit(self.centralwidget)
        self.data_length_Edit.setGeometry(QtCore.QRect(30, 400, 150, 25))
        self.data_length_Edit.setObjectName("chess_width_Edit")
        self.pushButton_save = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_save.setGeometry(QtCore.QRect(30, 440, 150, 25))
        self.pushButton_save.setObjectName("pushButton_save")
        self.pushButton_cancel = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_cancel.setGeometry(QtCore.QRect(30, 480, 150, 25))
        self.pushButton_cancel.setObjectName("pushButton_cancel")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 28))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
    def closeEvent(self, event):
        self.thread.stop()
        event.accept()
    def update_image(self, cv_img):
        """Updates the image_label with a new opencv image"""
        qt_img = self.convert_cv_qt(cv_img)
        self.img_label.setPixmap(qt_img)
    
    def convert_cv_qt(self, cv_img):
        """Convert from an opencv image to QPixmap"""
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QtGui.QImage(rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
        p = convert_to_Qt_format.scaled(431, 371, Qt.KeepAspectRatio)
        return QPixmap.fromImage(p)
    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.label.setText(_translate("MainWindow", "傾斜、擺動Chessboard"))
        self.pushButton.setText(_translate("MainWindow", "Display"))
        self.label_cameraID.setText(_translate("MainWindow", "CameraID"))
        self.cameraID_Edit.setText(_translate("MainWindow", ""))
        self.label_chess_width.setText(_translate("MainWindow", "ChessBoard方格寬度"))
        self.chess_width_Edit.setText(_translate("MainWindow", "2.2"))
        self.label_data_length.setText(_translate("MainWindow", "蒐集Data數量"))
        self.data_length_Edit.setText(_translate("MainWindow", "30"))        
        self.pushButton.clicked.connect(self.displayvideo)
        self.pushButton_save.setText(_translate("MainWindow", "save"))
        self.pushButton_cancel.setText(_translate("MainWindow", "close"))
        self.pushButton_save.clicked.connect(self.save_intrinsic)
        self.pushButton_cancel.clicked.connect(QtWidgets.QApplication.instance().quit)
    def displayvideo(self):
        cameraID = int(self.cameraID_Edit.text())
        chess_width = float(self.chess_width_Edit.text())
        data_length = float(self.data_length_Edit.text())
        self.thread = VideoThread(cameraID,chess_width,data_length)
        # connect its signal to the update_image slot
        self.thread.change_pixmap_signal.connect(self.update_image)
        self.thread.change_text_signal.connect(self.recordtext)
        # start the thread
        self.thread.start()
    def recordtext(self,text):
        groupBox = QtWidgets.QGroupBox()
        label1 = QLabel(text)
        self.formLayout.addRow(label1)
        groupBox.setLayout(self.formLayout)
        self.scrollArea.setWidget(groupBox)
        self.scrollArea.setWidgetResizable(True)
    def save_intrinsic(self):
        mtx = self.thread.mtx
        dist = self.thread.dist
        self.camera_intrinsic_dict(mtx, dist)
        text = "已經存取新的camera_intrinsic"
        self.recordtext(text)
    def camera_intrinsic_dict(self, mtx, dist):
        cameraID = int(self.cameraID_Edit.text())
        config_ = config
        [[fx,_,cx],[_,fy,cy],[_,_,_]] = mtx
        dict_ = eval(config['Camera_intrinsic']["cam"+str(cameraID)])
        dict_["mtx"] = [fx,fy,cx,cy]
        dict_["dist"] = dist.tolist()[0]
        config_['Camera_intrinsic'] = {"cam"+str(cameraID) : dict_}
        with open('config.ini', 'w') as configfile:
            config_.write(configfile) 
        
class ExecutechessGUI:
    def exec(self):
        import sys
        app = QtWidgets.QApplication(sys.argv)
        MainWindow = QtWidgets.QMainWindow()
        ui = Ui_MainWindow()
        ui.setupUi(MainWindow)
        MainWindow.show()
        app.exec_()
# import sys
# app = QtWidgets.QApplication(sys.argv)
# MainWindow = QtWidgets.QMainWindow()
# ui = Ui_MainWindow()
# ui.setupUi(MainWindow)
# MainWindow.show()
# app.exec_()