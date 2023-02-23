import numpy as np
from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QLabel
from PyQt5.QtCore import QThread, pyqtSignal, Qt, QSize
from PyQt5.QtGui import QImage, QPixmap, QMouseEvent
from PyQt5 import uic, QtCore
import sys
import cv2
"""
    class VideoFeed(QThread):
    img_update_res = pyqtSignal(QPixmap)
    def __init__(self):
        super().__init__()
        self.is_running = False
       
            def run(self):
        self.cap = cv2.VideoCapture(0)
        self.is_running = True
        while self.is_running:
            if self.stop_video:
                break
            ret, frame = self.cap.read()
            if ret:
                image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                flipped = cv2.flip(image, 1)

                h, w, ch = flipped.shape

                # hsv video feed
                hsv = cv2.cvtColor(flipped, cv2.COLOR_RGB2HSV)

                # Upper & Lower
                lower = np.array([1 - 4, 50, 50])
                upper = np.array([1 + 4, 255, 255])

                mask = cv2.inRange(hsv, lower, upper)
                result = cv2.bitwise_and(flipped, flipped, mask=mask)

                #result = cv2.cvtColor(result, cv2.COLOR_BGR2RGB)
                mask = cv2.cvtColor(mask, cv2.COLOR_GRAY2RGB)
                result = cv2.cvtColor(result, cv2.COLOR_BGR2RGB)
                # Convert to Qt format

                result_image = QImage(result.data, result.shape[1], result.shape[0], QImage.Format_RGB888)
                # pic = qt_image.scaled(640, 480, Qt.KeepAspectRatio)
                result_pixmap = QPixmap.fromImage(result_image)
                self.img_update_res.emit(result_pixmap)
    """



class VideoFeed(QThread):
    img_update = pyqtSignal(np.ndarray)
    def __init__(self):
        super().__init__()
        self.is_running = False

    def run(self):
        cap = cv2.VideoCapture(0)
        self.is_running = True
        while self.is_running:
            ret, frame = cap.read()
            if ret:
                self.img_update.emit(frame)
    def stop(self):
        self.is_running = False

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('color_seg_ui.ui', self)


        # Mouse clicked
        self.color_hover = np.zeros((250, 250, 3), np.uint8)
        self.color_selected = np.zeros((250, 250, 3), np.uint8)

        self.img_hsv = np.zeros((250, 250, 3), np.uint8)

        self.pixel = (250, 250, 3)
        # Labels
        self.video_thread = VideoFeed()
        self.video_thread.img_update.connect(self.set_video_frame)
        self.is_processing = False

        self.video_lbl = self.findChild(QLabel, 'label')
        self.video_lbl.setMouseTracking(True)
        #self.video_lbl.mouseMoveEvent = self.mouse_move_event
        #self.video_lbl.mousePressEvent = self.mouse_press_event

        self.video_result_lbl = self.findChild(QLabel, 'label_2')



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
        self.video_thread.start()

        self.play_btton.setEnabled(False)
        self.stop_btton.setEnabled(True)
    def stop_video(self):
        self.video_thread.stop()
        self.video_lbl.clear()
        self.video_result_lbl.clear()

        self.rgb_hover_lbl.setText(f"R:0  G:0  B:0")
        self.rgb_selected_lbl.setText(f"R:0  G:0  B:0")

        self.play_btton.setEnabled(True)
        self.stop_btton.setEnabled(False)
        """
        
        self.is_playing = False
        self.video_thread.stop_video = True
        self.video_thread.wait()
        self.video_lbl.clear()
        self.hover_color_lbl.clear()
        self.selected_color_lbl.clear()

        """

    def set_video_frame(self, frame):
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        flipped = cv2.flip(image, 1)

        # Convert to Qt format
        qt_image = QImage(flipped.data, flipped.shape[1], flipped.shape[0], QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qt_image)
        self.video_lbl.setPixmap(pixmap)







"""
    def mouse_move_event(self, event):
        if self.is_playing:
            x = event.x()
            y = event.y()
            qimg = self.video_lbl.pixmap().toImage()
            self.rgb = qimg.pixelColor(x, y)

            r, g, b = self.rgb.red(), self.rgb.green(), self.rgb.blue()
            self.color_hover[:] = (r, g, b)
            self.rgb_hover_lbl.setText(f"R:{r} G:{g} B:{b}")

            image = QImage(QSize(1, 1), QImage.Format_ARGB32_Premultiplied)
            image.setPixelColor(0, 0, self.rgb)
            pixmap = QPixmap.fromImage(image)
            self.findChild(QLabel, 'label_3').setPixmap(pixmap)
            
            
    def mouse_press_event(self, event):
        if self.is_playing:
            x = event.x()
            y = event.y()
            qimg = self.video_lbl.pixmap().toImage()
            rgb = qimg.pixelColor(x, y)
            self.rgb_glob = rgb
            r, g, b = rgb.red(), rgb.green(), rgb.blue()
            self.color_selected[:] = (r, g, b)
            self.rgb_selected_lbl.setText(f"R:{r} G:{g} B:{b}")

            image = QImage(QSize(1, 1), QImage.Format_ARGB32_Premultiplied)
            image.setPixelColor(0, 0, rgb)
            pixmap = QPixmap.fromImage(image)
            self.findChild(QLabel, 'label_4').setPixmap(pixmap)


    



            
            h, s, v, a = rgb.getHsv()

            #self.start_video_res

            ret, frame = self.video_thread.cap.read()


            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            lower = np.array([h - 4, 50, 50])
            upper = np.array([h + 4, 255, 255])

            mask = cv2.inRange(hsv, lower, upper)
            result = cv2.bitwise_and(frame, frame, mask=mask)

            result = cv2.cvtColor(result, cv2.COLOR_BGR2RGB)
            mask = cv2.cvtColor(mask, cv2.COLOR_GRAY2RGB)
            #print(result)
            result_pixmap = QPixmap.fromImage(QImage(result.data, result.shape[1], result.shape[0], QImage.Format_RGB888))
            self.video_result_lbl.setPixmap(result_pixmap)
            self.findChild(QLabel, 'label_2').setPixmap(pixmap)
            
            """


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
