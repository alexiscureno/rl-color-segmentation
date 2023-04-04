![OpenCV](https://img.shields.io/badge/opencv-%23white.svg?style=for-the-badge&logo=opencv&logoColor=white)
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Qt](https://img.shields.io/badge/Qt-%23217346.svg?style=for-the-badge&logo=Qt&logoColor=white)

# Video Color Segmentation
This is a Python application that uses OpenCV and PyQt5 to display live video feed from the webcam. The application also allows the user to select a color on the video feed by clicking on it. The program will then apply color segmentation to the video feed and display the result in real-time.

# Introduction
This program is a simple color segmentation application that allows the user to select a color from a video feed and apply a color filter on the video feed to show only that color.

# Requirements
*  Python 3.7 or later installed
* PyQt5
* Numpy
* OpenCV

# Installation
* Clone the repository or download the zip file
* Install the requirements using pip: pip install PyQt5 opencv-python
* Run the program using the command: python color_seg_app.py

# Usage
* When the program starts, click on the 'Start' button to start the video feed.
* Move the cursor over the video feed to see the RGB values of the pixel under the cursor.
* Click on a pixel to select a color.
* The program will apply a color filter on the video feed to show only the selected color.

# Files
* ui.py: The main Python file containing the application code.
* color_seg_ui.ui: The UI file for the application, created using the Qt Designer.
