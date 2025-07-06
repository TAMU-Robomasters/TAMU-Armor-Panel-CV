import cv2 as cv
import numpy as np
from frame_proccesing import *
from armour import *
from icon_detection import *
from PnP import *
from config import *

camera = cv.VideoCapture(0)

# Camera Configuration
camera.set(cv.CAP_PROP_FRAME_WIDTH, 640)
camera.set(cv.CAP_PROP_FRAME_HEIGHT, 480)
camera.set(cv.CAP_PROP_AUTOFOCUS, 0)
camera.set(cv.CAP_PROP_AUTOFOCUS, 100) # 50 ft or something idk
camera.set(cv.CAP_PROP_AUTO_EXPOSURE, 0.25)
camera.set(cv.CAP_PROP_EXPOSURE, -9.0) # tune before match

if not camera.isOpened():
    print("camera error")
    exit()

#main loop
while True:
    ret, frame = camera.read()

    if not ret:
        print("frame capture fail")
        break

    contours = frame_process(frame)
    bounding_boxes = bounding_boxes(contours, frame)
    if len(bounding_boxes) > 1:
        pairs = pair(bounding_boxes, frame)
        corners = armour_corners(pairs, frame)

        ids = icon_detection(corners, frame)

        cords = get_cord(corners)
    else:
        cords = []

    if DEBUG and ret:
        print(cords)
        cv.imshow(frame)