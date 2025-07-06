import cv2 as cv
import numpy as np
from config import DEBUG
import math

armor_height_ratio = 12.5/6


class Lights:
    def __init__(self, cx, cy, w, h, angle):
        self.cx = cx
        self.cy = cy
        self.w = w
        self.h = h
        self.angle = angle

def bounding_boxes(contours, frame):
    """
    creating bounding boxes around lights
    :param frame:
    :param contours:
    :return: list of bounding boxes
    """
    b_boxes = []
    for contour in contours:
        rect = cv.minAreaRect(contour)
        w_holder, h_holder = rect[1]

        if w_holder > h_holder:
            h, w = rect[1]
        else:
            w,h = rect[1]

        area = w*h

        angle = rect[2]
        if w_holder > h_holder:
            angle += 90

        if ((abs(angle-90) > 45)):
            continue
        else:
            if DEBUG:
                box = cv.boxPoints(rect)    # Get 4 corner points of the rotated box
                box = np.intp(box)           # Convert to integer for drawing
                cv.drawContours(frame, [box], 0, (0, 255, 0), 2)
            b_box = Lights(rect[0][0], rect[0][1], w, h, angle)
            b_boxes.append(b_box)

    return b_boxes

def pair(b_boxes, frame):
    """
    Pairs lights together based off of score

    :param b_boxes:
    :param frame:
    :return: list of pairs of lights
    """
    pairs = []
    if len(b_boxes) > 1:
        for i in range(len(b_boxes)):
            if b_boxes[i] != None:
                scores = []
                for j in range(len(b_boxes)):
                    if j != i and b_boxes[j] != None:
                        try:
                            light1 = b_boxes[i]
                            light2 = b_boxes[j]
                            angle_diff = abs(light1.angle - light2.angle)
                            misalignment_angle = abs(np.degrees((np.arctan((light1.cy - light2.cy)/ (light1.cx - light2.cx)))))
                            average_height = (light1.h + light2.h) / 2
                            distance = np.sqrt((light1.cx - light2.cx)**2 + (light1.cy - light2.cy)**2)
                            expected_distance = abs((average_height / (5.5/13)) - distance)
                            hr = light1.h / light2.h

                            score = angle_diff + misalignment_angle + expected_distance + hr
                            scores.append(score)
                        except:
                            pass
                try:
                    if min(scores) < 70:
                        minimum_score_index = scores.index(min(scores))
                        pairs.append([b_boxes[i], b_boxes[i+1+minimum_score_index]])
                        b_boxes[minimum_score_index] = None
                except:
                    pass
            b_boxes[i] = None

    return pairs

def armour_corners(pairs, frame):
    """
    an absolute monster of math. 
    :param pairs: list of pairs
    :param frame:
    :return: list of 4 points
    """
    list_of_points = []
    for pair in pairs:
        if (pair[0].cx <= pair[1].cx):
            left = pair[0]
            right = pair[1]
        else:
            left = pair[1]
            right = pair[0]

        #
        top_left = [int(left.cx + left.w * 0.5 - (left.h * armor_height_ratio) * 0.5 * math.cos(
            math.radians(left.angle))), int((left.cy - (
                    (left.h * armor_height_ratio) * 0.5 * math.sin(math.radians(left.angle)))))]
        top_right = [int(right.cx - right.w * 0.5 - (right.h * armor_height_ratio) * 0.5 * math.cos(
            math.radians(right.angle))), int((right.cy - (
                    (right.h * armor_height_ratio) * 0.5 * math.sin(math.radians(right.angle)))))]
        bottom_left = [int(left.cx + left.w * 0.5 + (left.h * armor_height_ratio) * 0.5 * math.cos(
            math.radians(left.angle))), int((left.cy + (
                    (left.h * armor_height_ratio) * 0.5 * math.sin(math.radians(left.angle)))))]
        bottom_right = [int(
            right.cx - right.w * 0.5 + (right.h * armor_height_ratio) * 0.5 * math.cos(
                math.radians(right.angle))), int((right.cy + (
                    (right.h * armor_height_ratio) * 0.5 * math.sin(math.radians(right.angle)))))]

        points = np.array([top_left, top_right, bottom_right, bottom_left], dtype=np.int32)
        points = points.reshape((-1, 1, 2))
        
        if DEBUG:
            cv.polylines(frame, [points], True, (255, 255, 255), 2)
        
        list_of_points.append(points)
    return list_of_points
        