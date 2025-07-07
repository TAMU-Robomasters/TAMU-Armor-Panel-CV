import cv2 as cv
import numpy as np
from config import DEBUG
import os

expected_points = np.float32([[0, 0], [300, 0], [300, 300], [0, 300]])

folder_path = "TAMU-Armor-Panel-CV\\icons"
icon_list = []
for pic in os.listdir(folder_path):
    full_path = os.path.join(folder_path, pic)
    picture = cv.imread(full_path)
    gray = cv.cvtColor(picture, cv.COLOR_BGR2GRAY)
    icon_list.append(gray)

def icon_detection(list_of_points, list_of_centers, frame): # TODO: change list_of_points and list_of_centers to a 'panels' class
    """
    transforms and crops out armour panels to compare to icons
    :param frame:
    :param list_of_points:
    :return: list of ids, 0 = 1 (hero), 1 = 3 (standard), 2 = sentry
    """
    ids = []
    for points in list_of_points:
        points = np.float32(points)

        M = cv.getPerspectiveTransform(points, expected_points)

        warped = cv.warpPerspective(frame, M, (300, 300))

        warped = cv.cvtColor(warped, cv.COLOR_BGR2GRAY)

        adaptive_tresh = cv.adaptiveThreshold(warped, 255, cv.ADAPTIVE_THRESH_MEAN_C, cv.THRESH_BINARY, 41, -6)

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
        for pic in icon_list:
            compared = cv.bitwise_xor(pic, resized)
            icon_scores.append(int(100 * (1 - (np.sum(compared == 255) / 300 ** 2))))
        # 0 - 1, 1 - 3, 2 - sentry
        id = icon_scores.index(max(icon_scores))
        ids.append(id)  

        if DEBUG:
            cv.rectangle(adaptive_tresh,(x,y),(x+w,y+h),(255,255,255),2)
        
            if(id == 0):
                str_holder = "Hero"
            elif(id == 1):
                str_holder = "Standard"
            else:
                str_holder = "Sentry"
            for center in list_of_centers:
                cv.putText(frame, str_holder, (center[0]-25, center[1]+25), cv.FONT_HERSHEY_SIMPLEX, 0.5, (100,255,255), 1)

    return ids