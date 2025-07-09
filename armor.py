import cv2 as cv
import numpy as np
import math
from config import DEBUG

armor_height_ratio = 12.5/5.2
armor_width_ration = 5.5/13


class Lights:
    def __init__(self, cx, cy, w, h, angle):
        self.cx = cx
        self.cy = cy
        self.w = w
        self.h = h
        self.angle = angle

class Panel:
    def __init__(self, corners, center):
        self.corners = corners
        self.center = center
        self.tvec = None
        self.rvec = None
        self.id = -1

def bounding_boxes(contours, frame):
    """
    creating bounding boxes around lights
    :param frame:
    :param contours:
    :return: list of bounding boxes
    """
    b_boxes = []
    for contour in contours:# have to keep
        rect = cv.minAreaRect(contour)
        h_holder, w_holder = rect[1]

        if rect[1][0] > rect[1][1]:
            h,w = rect[1]
        else:
            w,h = rect[1]

        area = w*h

        angle = rect[2]
        if w_holder > h_holder:
            angle += 90

        # filter out bad detections: true if bad
        if ((abs(angle-90) > 45)):
            continue
        else:
            if DEBUG:
                box = cv.boxPoints(rect)  # Get 4 corner points of the rotated box
                box = np.intp(box)  # Convert to integer for drawing
                cv.drawContours(frame, [box], 0, (0, 255, 0), 2)
            b_box = Lights(rect[0][0], rect[0][1], w, h, angle)
            b_boxes.append(b_box)

    return b_boxes

def pair(b_boxes):
    """
    Pairs lights together based off of score

    :param b_boxes:
    :param frame:
    :return: list of pairs of lights
    """
    print(b_boxes[0].angle)
    pairs = []
    if len(b_boxes) > 1:
        for i in range(len(b_boxes)):#have to keep
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
                            expected_distance = abs((average_height / armor_width_ration) - distance)
                            hr = light1.h / light2.h

                            score = angle_diff + misalignment_angle + expected_distance + hr
                            # score = angle_diff + misalignment_angle + hr
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

def armour_corners(pair):
    """
    an absolute monster of math. 
    :param pairs: list of pairs
    :param frame:
    :return: list of 4 points
    """
    # Since pair is a list of two Lights objects
    light1, light2 = pair[0], pair[1]
    # Determine left and right lights based on x-coordinate
    if light1.cx <= light2.cx:
        left = light1
        right = light2
    else:
        left = light2
        right = light1

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

    panel_center = np.array([((top_left[0]+bottom_left[0]+top_right[0]+bottom_right[0])/4), (top_left[1]+bottom_left[1]+top_right[1]+bottom_right[1])/4], dtype=np.int32)

    panel = Panel(points, panel_center)

    return panel