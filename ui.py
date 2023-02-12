import numpy as np
from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QLabel
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtGui import QImage, QPixmap, QMouseEvent
from PyQt5 import uic, QtCore
import sys
import cv2

class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()
        #self.videofeed = None
        uic.loadUi('color_seg_ui.ui', self)

        # Mouse clicked
        self.color_hover = np.zeros((250, 250, 3), np.uint8)
        self.color_selected = np.zeros((250, 250, 3), np.uint8)

        self.img_hsv = (250, 250, 3)
        self.pixel = (250, 250, 3)

        # Labels
        self.origin_img_lbl = self.findChild(QLabel, 'label')
        self.origin_img_lbl.setMouseTracking(True)
        self.origin_img_lbl.mouseMoveEvent = self.mouse_event
        self.result_img_lbl = self.findChild(QLabel, 'label_2')

        # Buttons
        self.play_btton = self.findChild(QPushButton, 'pushButton')
        self.play_btton.clicked.connect(self.start_video)

        self.stop_btton = self.findChild(QPushButton, 'pushButton_2')
        self.stop_btton.clicked.connect(self.Cancelbutton)

    def mouse_event(self, event):

        #if event.buttons() == QtCore.Qt.MouseEventSource:
        #print("Simple mouse motion")
        #
        label_position = self.origin_img_lbl.mapFrom(self, event.pos())
        x = label_position.x()
        y = label_position.y()
        print(x, y)

        """
        x, y = event.x(), event.y()
        ret, img = self.cap.read()
        if ret:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            #flip = cv2.flip(img, 1)
            B, G, R = img[y, x]
        """
    def mousePressEvent(self, QMouseEvent):
        if QMouseEvent.button() == Qt.LeftButton:
            print("Left Button Clicked")

    def show_color(self, event, x, y, flags, params):

        self.B = self.img[y, x][0]
        self.G = self.img[y, x][1]
        self.R = self.img[y, x][2]
        self.color_hover[:] = (self.B, self.G, self.R)

        if event == cv2.EVENT_LBUTTONDOWN:
            self.pixel = self.img_hsv[y, x]
            self.color_selected[:] = (self.B, self.G, self.R)
            print(self.pixel)
        if event == cv2.EVENT_RBUTTONDOWN:
            self.B = self.color_selected[10, 10][0]
            self.G = self.color_selected[10, 10][1]
            self.R = self.color_selected[10, 10][2]

        #cv2.setMouseCallback('MainWindow', self.show_color)

    def start_video(self):
        self.videofeed = VideoFeed()
        self.videofeed.start()
        self.videofeed.img_update.connect(self.ImageupdateSlot)

    def ImageupdateSlot(self, Image):
        self.origin_img_lbl.setPixmap(QPixmap.fromImage(Image))

    def Cancelbutton(self):
        self.videofeed.stop()

class VideoFeed(QThread):
    img_update = pyqtSignal(QImage)

    def run(self):
        self.ThreadActive = True
        self.cap = cv2.VideoCapture(0)
        while self.ThreadActive:
            self.ret, self.img = self.cap.read()
            if self.ret:
                image = cv2.cvtColor(self.img, cv2.COLOR_BGR2RGB)
                flip = cv2.flip(image, 1)

                # Convert to Qt format
                qt_image = QImage(flip.data, flip.shape[1], flip.shape[0], QImage.Format_RGB888)
                pic = qt_image.scaled(640, 480, Qt.KeepAspectRatio)
                self.img_update.emit(pic)

    def stop(self):
        self.ThreadActive = False
        #self.quit()

if __name__ == "__main__":

    app = QApplication(sys.argv)
    UIWindow = MainWindow()
    UIWindow.show()
    sys.exit(app.exec())
