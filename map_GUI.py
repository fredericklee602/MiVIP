# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'map.ui'
#
# Created by: PyQt5 UI code generator 5.14.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets
import cv2
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt, QThread
from PyQt5.QtGui import QPixmap,QImage
import numpy as np
import random
from DB_SQL import DB_connect

class DisplayThread(QThread):
    change_pixmap_signal = pyqtSignal(np.ndarray)
    def __init__(self,displayshape,real_w,real_h):
        super().__init__()
        self.displayshape = displayshape
        self._run_flag = True
        self.img1 = cv2.imread("roommap.png")
        self.img1 = cv2.resize(self.img1,self.displayshape)
        self.img2 = cv2.imread("person.png")
        self.img2 = cv2.resize(self.img2,(20,20))
        self.real_w = real_w
        self.real_h = real_h
        # MYSQL DB
        self.DBCONN = DB_connect()
    def imageprocess(self):
        copyIma = self.img2.copy()
        h, w = self.img2.shape[:2]
        mask = np.zeros([h+2, w+2], np.uint8)
        cv2.floodFill(copyIma, mask, (0, 0), (255, 255, 255), (100, 100, 100), (50, 50, 50), cv2.FLOODFILL_FIXED_RANGE) 
        img2gray = cv2.cvtColor(copyIma,cv2.COLOR_BGR2GRAY)
        ret, mask = cv2.threshold(img2gray, 254, 255, cv2.THRESH_BINARY)
        rows, cols, channels = self.img2.shape
        return rows, cols, mask

    def cal_img_2D_coordainte(self,coordinate):
        h = self.img1.shape[0]
        w = self.img1.shape[1]
        r_w,r_h = self.real_w, self.real_h
        scale_h = h/int(r_h)
        scale_w = w/int(r_w)
        x = coordinate[0][0] * scale_w
        y = coordinate[1][0] * scale_h
        return [int(x),int(y)]
    def run(self):
        rows, cols, mask = self.imageprocess()
        while self._run_flag:

            data = self.DBCONN.SelectNewCoordinate()
            copyIma1 = self.img1.copy()
            for raw in data:
                objectname = raw["objectname"]
                coordinate = raw["coordinate"]
                if objectname=="head":
                    [x,y] = self.cal_img_2D_coordainte(eval(coordinate))
                    if x < 0:
                        x = 0
                    if y < 0:
                        y = 0
                    if x > self.img1.shape[1]-cols:
                        x = self.img1.shape[1]-cols
                    if y > self.img1.shape[0]-rows:
                        y = self.img1.shape[0]-rows
                    roi = self.img1[y:y+rows, x:x+cols]
                    
                    img1_bg = cv2.bitwise_and(roi, roi, mask = mask)
                    mask_inv = cv2.bitwise_not(mask)
                    img2_fg = cv2.bitwise_and(self.img2, self.img2, mask = mask_inv)
                    dst = cv2.add(img1_bg,img2_fg)
                    copyIma1[y:y+rows, x:x+cols] = dst
                    cv_img = copyIma1
            try:
                self.change_pixmap_signal.emit(cv_img)
            except:
                return
class Ui_MainWindow(object):
    def __init__(self):
        self.displayshape = (701, 391)
        self.img = cv2.imread('roommap.png')
        self.img = self.img
        self.img = cv2.resize(self.img,self.displayshape)
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.label_map = QtWidgets.QLabel(self.centralwidget)
        height, width, bytesPerComponent = self.img.shape
        bytesPerLine = 3 * width
        cv2.cvtColor(self.img, cv2.COLOR_BGR2RGB, self.img)
        QImg = QImage(self.img.data, width, height, bytesPerLine,QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(QImg)
        self.label_map.setPixmap(pixmap)
        self.label_map.setCursor(Qt.CrossCursor)
        self.label_map.setGeometry(QtCore.QRect(50, 30, self.displayshape[0], self.displayshape[1]))
        self.label_map.setText("")
        self.label_map.setObjectName("label_map")
        self.scrollArea_object_text = QtWidgets.QScrollArea(self.centralwidget)
        self.scrollArea_object_text.setGeometry(QtCore.QRect(49, 439, 311, 101))
        self.scrollArea_object_text.setWidgetResizable(True)
        self.scrollArea_object_text.setObjectName("scrollArea_object_text")
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 309, 99))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.scrollArea_object_text.setWidget(self.scrollAreaWidgetContents)
        self.label_h_w = QtWidgets.QLabel(self.centralwidget)
        self.label_h_w.setGeometry(QtCore.QRect(440, 440, 121, 17))
        self.label_h_w.setObjectName("label_h_w")
        self.textEdit_h_w = QtWidgets.QLineEdit(self.centralwidget)
        self.textEdit_h_w.setGeometry(QtCore.QRect(440, 470, 101, 31))
        self.textEdit_h_w.setObjectName("textEdit_h_w")
        self.submitButton = QtWidgets.QPushButton(self.centralwidget)
        self.submitButton.setGeometry(QtCore.QRect(440, 510, 101, 25))
        self.submitButton.setObjectName("submitButton")
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

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.label_h_w.setText(_translate("MainWindow", "空間實際寬高(cm)"))
        self.submitButton.setText(_translate("MainWindow", "Submit"))
        self.textEdit_h_w.setText(_translate("MainWindow", "480,220")) 
        self.submitButton.clicked.connect(self.displayvideo)  
    
    def update_image(self, cv_img):
        """Updates the image_label with a new opencv image"""
        qt_img = self.convert_cv_qt(cv_img)
        self.label_map.setPixmap(qt_img)
    
    def convert_cv_qt(self, cv_img):
        """Convert from an opencv image to QPixmap"""
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QtGui.QImage(rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
        p = convert_to_Qt_format.scaled(self.displayshape[0], self.displayshape[1], Qt.KeepAspectRatio)
        return QPixmap.fromImage(p)

    def displayvideo(self):
        real_w,real_h = self.textEdit_h_w.text().split(",")
        self.thread = DisplayThread(self.displayshape,real_w,real_h)
        # connect its signal to the update_image slot
        self.thread.change_pixmap_signal.connect(self.update_image)
        # start the thread
        self.thread.start()


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    # ui.displayvideo()
    sys.exit(app.exec_())
