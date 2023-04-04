import numpy as np
from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QLabel
from PyQt5.QtCore import QThread, pyqtSignal, Qt, QSize
from PyQt5.QtGui import QImage, QPixmap, QMouseEvent
from PyQt5 import uic, QtCore
import sys
import cv2

# Define a trhead for video feed
class VideoFeed(QThread):
    # Define a signal for updating the image in the UI
    img_update = pyqtSignal(np.ndarray)
    def __init__(self):
        super().__init__()
        self.is_running = False

    # Define the run method that is called when the thread is started
    def run(self):
        # Initialize the video capture
        cap = cv2.VideoCapture(0)
        # Loop until the thread is stopped
        self.is_running = True
        while self.is_running:
            # Read a frame from the video capture
            ret, frame = cap.read()
            # If a frame is successfully read, emit the signal with the frame data
            if ret:
                self.img_update.emit(frame)

    # Define a method for stopping the thread
    def stop(self):
        self.is_running = False
# Define the main window class
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # Load the UI file
        uic.loadUi('color_seg_ui.ui', self)

        # Initialize variables for the selected and hovered colors, and the HSV image
        self.color_hover = np.zeros((250, 250, 3), np.uint8)
        self.color_selected = np.zeros((250, 250, 3), np.uint8)
        self.img_hsv = np.zeros((250, 250, 3), np.uint8)

        # Initialize other variables for the UI
        self.rgb_glob = (250, 250, 3)

        self.video_thread = VideoFeed()
        self.video_thread.img_update.connect(self.set_video_frame)
        self.is_processing = False
        self.is_playing = False
        self.is_color = False

        # Initialize the labels in the UI and enable mouse tracking on the video label
        self.video_lbl = self.findChild(QLabel, 'label')
        self.video_lbl.setMouseTracking(True)
        self.video_lbl.mouseMoveEvent = self.mouse_move_event
        self.video_lbl.mousePressEvent = self.mouse_press_event

        self.video_result_lbl = self.findChild(QLabel, 'label_2')

        self.hover_color_lbl = self.findChild(QLabel, 'label_3')
        self.selected_color_lbl = self.findChild(QLabel, 'label_4')

        self.rgb_hover_lbl = self.findChild(QLabel, 'rgb_hover_label')
        self.rgb_selected_lbl = self.findChild(QLabel, "rgb_selected_label")

        # Initialize the buttons in the UI and connect them to their corresponding methods
        self.play_btton = self.findChild(QPushButton, 'pushButton')
        self.play_btton.clicked.connect(self.start_video)

        self.stop_btton = self.findChild(QPushButton, 'pushButton_2')
        self.stop_btton.clicked.connect(self.stop_video)
        self.stop_btton.setEnabled(False)

    # Method for starting the video feed thread
    def start_video(self):
        self.is_playing = True
        self.video_thread.start()

        self.play_btton.setEnabled(False)
        self.stop_btton.setEnabled(True)

    # Method for stopping the video feed thread
    def stop_video(self):
        self.is_playing = False
        self.video_thread.stop()
        self.video_thread.wait()
        self.video_lbl.clear()
        self.video_result_lbl.clear()
        self.hover_color_lbl.clear()
        self.selected_color_lbl.clear()
        self.rgb_hover_lbl.setText(f"R:0  G:0  B:0")
        self.rgb_selected_lbl.setText(f"R:0  G:0  B:0")

        self.play_btton.setEnabled(True)
        self.stop_btton.setEnabled(False)

    def set_video_frame(self, frame):
        """
        Updates the displayed video frame with the given frame.

        :param frame: The video fram to display
        :return:
        """
        if self.is_playing:
            # Convert to RGB format and flip the image horizontally
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            flipped = cv2.flip(image, 1)

            # Convert to Qt format and display in video_lbl
            qt_image = QImage(flipped.data, flipped.shape[1], flipped.shape[0], QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(qt_image)
            self.video_lbl.setPixmap(pixmap)

        if self.is_color:
            # Extract the HSV values of the selected color and create a mask of pixels within a certain range
            h, s, v, a = self.rgb_glob.getHsv()
            hsv = cv2.cvtColor(flipped, cv2.COLOR_RGB2HSV)

            # Set lower and upper bounds for the color filtering
            lower = np.array([(h / 2) - 5, 50, 50])
            upper = np.array([(h / 2) + 5, 255, 255])

            # Apply the mask to the original image and display the resulting image in video_result_lbl
            mask = cv2.inRange(hsv, lower, upper)
            result = cv2.bitwise_and(flipped, flipped, mask=mask)


            # Convert result to pixmap and display it
            #result = cv2.cvtColor(result, cv2.COLOR_BGR2RGB)
            mask = cv2.cvtColor(mask, cv2.COLOR_GRAY2RGB)
            result_pixmap = QPixmap.fromImage(QImage(result.data, result.shape[1], result.shape[0], QImage.Format_RGB888))
            self.video_result_lbl.setPixmap(result_pixmap)


    def mouse_move_event(self, event):
        # Only perform the action if video is playing
        if self.is_playing:
            # Get x,y coordinates of mouse pointer
            x = event.x()
            y = event.y()

            # Get color of pixel at x,y position on the video frame
            qimg = self.video_lbl.pixmap().toImage()
            rgb = qimg.pixelColor(x, y)

            # Extract the RGB values from the pixel color
            r, g, b = rgb.red(), rgb.green(), rgb.blue()
            # Update the color_hover attribute with the RGB values
            self.color_hover[:] = (r, g, b)
            # Display the RGB values in a label
            self.rgb_hover_lbl.setText(f"R:{r} G:{g} B:{b}")

            # Create a small image with the selected color and display it in a label
            image = QImage(QSize(1, 1), QImage.Format_ARGB32_Premultiplied)
            image.setPixelColor(0, 0, rgb)
            pixmap = QPixmap.fromImage(image)
            self.findChild(QLabel, 'label_3').setPixmap(pixmap)

    def mouse_press_event(self, event):
        # Set is_color flag to True
        self.is_color = True
        # Only perform the action if video is playing
        if self.is_playing:
            # Get x,y coordinates of mouse pointer
            x = event.x()
            y = event.y()
            # Get color of pixel at x,y position on the video frame
            qimg = self.video_lbl.pixmap().toImage()
            rgb = qimg.pixelColor(x, y)
            # Store the selected color in rgb_glob attribute
            self.rgb_glob = rgb
            # Extract the RGB values from the pixel color
            r, g, b = rgb.red(), rgb.green(), rgb.blue()
            # Update the color_selected attribute with the RGB values
            self.color_selected[:] = (r, g, b)
            # Display the RGB values in a label
            self.rgb_selected_lbl.setText(f"R:{r} G:{g} B:{b}")

            # Create a small image with the selected color and display it in a label
            image = QImage(QSize(1, 1), QImage.Format_ARGB32_Premultiplied)
            image.setPixelColor(0, 0, rgb)
            pixmap = QPixmap.fromImage(image)
            self.findChild(QLabel, 'label_4').setPixmap(pixmap)

# Entry point of the application
if __name__ == '__main__':
    # Create a QApplication instance
    app = QApplication(sys.argv)
    # Create a MainWindow instance and show it
    window = MainWindow()
    window.show()
    # Run the application event loop
    sys.exit(app.exec_())
