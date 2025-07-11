import cv2 as cv
import numpy as np
from config import DEBUG
import os

expected_points = np.float32([[0, 0], [300, 0], [300, 300], [0, 300]])

folder_path = "icons"
icon_list = []
for pic in os.listdir(folder_path):
    full_path = os.path.join(folder_path, pic)
    picture = cv.imread(full_path)
    gray = cv.cvtColor(picture, cv.COLOR_BGR2GRAY)
    icon_list.append(gray)
def icon_detection(panel, frame):
    """
    transforms and crops out armour panels to compare to icons
    :param frame:
    :param list_of_points:
    :return: list of ids, 0 = 1 (hero), 1 = 3 (standard), 2 = sentry
    """

    points = panel.corners
    points = np.float32(points)

    M = cv.getPerspectiveTransform(points, expected_points)

    warped = cv.warpPerspective(frame, M, (300, 300))

    warped = cv.cvtColor(warped, cv.COLOR_BGR2GRAY)

    adaptive_tresh = cv.adaptiveThreshold(warped, 255, cv.ADAPTIVE_THRESH_MEAN_C, cv.THRESH_BINARY, 101, -1)

    icon_contours, _ = cv.findContours(adaptive_tresh, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)

    # find the biggest countour (c) by the area
    try:
        c = max(icon_contours[2:], key=cv.contourArea)
    except:
        pass

    x,y,w,h = cv.boundingRect(c)

    icon_scores = []
    cropped = adaptive_tresh[y:y+h, x:x+w]
    resized = cv.resize(cropped, (300,300))
    i = 0
    for pic in icon_list:
        compared = cv.bitwise_xor(pic, resized)
        if DEBUG:
            cv.imshow(f"icon + {i}", compared)
            i += 1
        average_intensity = cv.mean(compared)[0]
        icon_scores.append(average_intensity)
    # 0 - 1, 1 - 3, 2 - sentry
    if min(icon_scores) > 100:
        return False
    else:
        id = icon_scores.index(min(icon_scores))
        panel.id = id
        return True