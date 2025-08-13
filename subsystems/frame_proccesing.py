import cv2 as cv
import numpy as np

import config
from config import *

def frame_process(frame):
    """
    function will split color channels, threshold, and find contours.
    :param frame: input frame
    :param enemy_color: color of the enemy
    :return: contours
    """

    if (ENEMY_COLOR == 'BLUE'):
        _, thresh = cv.threshold(frame[:,:,0], config.blue_thresh[0], config.blue_thresh[1], cv.THRESH_BINARY) # tune before match
    elif (ENEMY_COLOR == 'RED'):
        _, thresh = cv.threshold(frame[:,:,2], config.red_thresh[0], config.red_thresh[1], cv.THRESH_BINARY) # tune before match
    else:
        print('invalid color')

    kernel = np.ones((3,3),np.uint8)
    closing = cv.morphologyEx(thresh, cv.MORPH_CLOSE, kernel)

    contours, _ = cv.findContours(closing, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)

    return contours