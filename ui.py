import numpy as np
from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QLabel
from PyQt5.QtCore import QThread, pyqtSignal, Qt, QSize
from PyQt5.QtGui import QImage, QPixmap, QMouseEvent
from PyQt5 import uic, QtCore
import sys
import cv2


class VideoFeed(QThread):
    img_update = pyqtSignal(QPixmap)

    def __init__(self):
        super().__init__()
        self.cap = cv2.VideoCapture(0)
        self.stop_video = False

    def run(self):
        while True:
            if self.stop_video:
                break
            ret, img = self.cap.read()
            if ret:
                image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                flip = cv2.flip(image, 1)
                h, w, ch = flip.shape
                # Convert to Qt format
                qt_image = QImage(flip.data, w, h, QImage.Format_RGB888)
                # pic = qt_image.scaled(640, 480, Qt.KeepAspectRatio)
                pixmap = QPixmap.fromImage(qt_image)
                self.img_update.emit(pixmap)

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi('color_seg_ui.ui', self)

        # Mouse clicked
        self.color_hover = np.zeros((250, 250, 3), np.uint8)
        self.color_selected = np.zeros((250, 250, 3), np.uint8)

        # Labels

        self.video_lbl = self.findChild(QLabel, 'label')
        self.video_lbl.setMouseTracking(True)
        self.video_lbl.mouseMoveEvent = self.mouseMoveEvent
        self.video_lbl.mousePressEvent = self.mousePressEvent

        self.video_thread = None
        self.is_playing = False

        self.hover_color_lbl = self.findChild(QLabel, 'label_3')
        self.selected_color_lbl = self.findChild(QLabel, 'label_4')


        self.rgb_hover_lbl = self.findChild(QLabel, 'rgb_hover_label')
        self.rgb_selected_lbl = self.findChild(QLabel, "rgb_selected_label")

        # Buttons
        self.play_btton = self.findChild(QPushButton, 'pushButton')
        self.play_btton.clicked.connect(self.start_video)

        self.stop_btton = self.findChild(QPushButton, 'pushButton_2')
        self.stop_btton.clicked.connect(self.stop_video)
        self.stop_btton.setEnabled(False)

    def start_video(self):
        self.is_playing = True
        self.video_thread = VideoFeed()
        self.video_thread.img_update.connect(self.set_video_frame)
        self.video_thread.start()

        self.play_btton.setEnabled(False)
        self.stop_btton.setEnabled(True)

    def stop_video(self):
        self.is_playing = False
        self.video_thread.stop_video = True
        self.video_thread.wait()
        self.video_lbl.clear()
        self.hover_color_lbl.clear()
        self.selected_color_lbl.clear()

        self.rgb_hover_lbl.setText(f"R:0  G:0  B:0")
        self.rgb_selected_lbl.setText(f"R:0  G:0  B:0")

        self.play_btton.setEnabled(True)
        self.stop_btton.setEnabled(False)

    def set_video_frame(self, pixmap):
        if self.is_playing:
            self.video_lbl.setPixmap(pixmap)
            self.video_lbl.setMouseTracking(True)

    def mouseMoveEvent(self, event):
        if self.is_playing:
            x = event.x()
            y = event.y()
            qimg = self.video_lbl.pixmap().toImage()
            rgb = qimg.pixelColor(x, y)

            r, g, b = rgb.red(), rgb.green(), rgb.blue()
            self.color_hover[:] = (r, g, b)
            self.rgb_hover_lbl.setText(f"R:{r} G:{g} B:{b}")

            image = QImage(QSize(1, 1), QImage.Format_ARGB32_Premultiplied)
            image.setPixelColor(0, 0, rgb)
            pixmap = QPixmap.fromImage(image)
            self.findChild(QLabel,'label_3').setPixmap(pixmap)

    def mousePressEvent(self, event):
        if self.is_playing:
            x = event.x()
            y = event.y()
            qimg = self.video_lbl.pixmap().toImage()
            rgb = qimg.pixelColor(x, y)

            r, g, b = rgb.red(), rgb.green(), rgb.blue()
            self.color_selected[:] = (r, g, b)
            self.rgb_selected_lbl.setText(f"R:{r} G:{g} B:{b}")

            image = QImage(QSize(1, 1), QImage.Format_ARGB32_Premultiplied)
            image.setPixelColor(0, 0, rgb)
            pixmap = QPixmap.fromImage(image)
            self.findChild(QLabel, 'label_4').setPixmap(pixmap)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
