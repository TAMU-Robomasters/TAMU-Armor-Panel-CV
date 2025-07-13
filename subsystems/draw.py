import cv2 as cv
import numpy as np

import config


def draw(panel, frame):
    cv.polylines(frame, [panel.corners], True, (255, 255, 255), 2)
    id = panel.id
    if (id == 0 or id == 1):
        str_holder = "Sentry"
    elif (id == 3):
        str_holder = "hero"
    elif (id == 2):
        str_holder = "standard"
    else:
        str_holder = "Unknown"
    center = panel.center
    cv.putText(frame, str_holder, (center[0] - 25, center[1] + 25), cv.FONT_HERSHEY_SIMPLEX, 0.5, (100, 255, 255),
               1)
    cv.putText(frame, ('tvec: ' + str(int(panel.tvec[0])) + ' ' + str(int(-1*panel.tvec[1])) + ' ' + str(int(panel.tvec[2]))),
               (center[0] - 25, center[1] + 50), cv.FONT_HERSHEY_SIMPLEX, 0.5, (100, 255, 255), 1)
    cv.putText(frame, ('rvec: ' + str(int(np.degrees(panel.rvec[0]))) + ' ' + str(int(np.degrees(panel.rvec[1]))) + ' ' + str(int(np.degrees(panel.rvec[2])))),
               (center[0] - 25, center[1] + 75),
               cv.FONT_HERSHEY_SIMPLEX, 0.5, (100, 255, 255), 1)
    cv.drawFrameAxes(frame, config.cam_matrix, config.dist, panel.rvec, panel.tvec, 5)