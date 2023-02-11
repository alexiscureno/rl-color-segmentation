import cv2
import numpy as np


color_hover = np.zeros((250, 250, 3), np.uint8)
color_selected = np.zeros((250, 250, 3), np.uint8)

img_hsv = (250, 250, 3)
pixel = (250, 250, 3)

cap = cv2.VideoCapture(0)


def show_color(event, x, y, flags, params):
    global pixel
    #
    B = img[y, x][0]
    G = img[y, x][1]
    R = img[y, x][2]

    color_hover[:] = (B, G, R)
    #

    if event == cv2.EVENT_LBUTTONDOWN:
        pixel = img_hsv[y, x]
        #print(pixel)

        color_selected[:] = (B, G, R)
    if event == cv2.EVENT_RBUTTONDOWN:
        B = color_selected[10, 10][0]
        G = color_selected[10, 10][1]
        R = color_selected[10, 10][2]


cv2.namedWindow('image')
cv2.setMouseCallback('image', show_color)

while (True):

    _, img = cap.read()
    img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    lower = np.array([pixel[0] - 4, 50, 50])
    upper = np.array([pixel[0] + 4, 255, 255])

    mask = cv2.inRange(img_hsv, lower, upper)
    result = cv2.bitwise_and(img, img, mask=mask)

    mask = cv2.cvtColor(mask, cv2.COLOR_GRAY2RGB)

    colors = np.hstack([color_hover, color_selected])

    cv2.imshow('image', img)
    cv2.imshow('color_hover', color_hover)
    cv2.imshow('color_selected', color_selected)

    # cv2.imshow('HSV result', img_hsv)
    cv2.imshow('mask', mask)
    cv2.imshow('result', result)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break