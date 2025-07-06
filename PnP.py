import cv2 as cv
import numpy as np

dist = np.load("calibration/dist.pkl", allow_pickle=True)
cam_matrix = np.load("calibration/cameraMatrix.pkl", allow_pickle=True)
panel_coordinates = np.array([(-12.3/2, 12.4/2, 0),
                              (12.3/2, 12.4/2, 0),
                              (12.3/2, -12.4/2, 0),
                              (-12.3/2, -12.4/2, 0)])

def get_cord(list_of_points):
    """
    Use PnP to find tvec and rvec of panels
    :param list_of_points:
    :return: [[tvec, rvec], ...]
    """
    cords = []
    if len(list_of_points) > 0:
        for points in list_of_points:
            success, rvec, tvec = cv.solvePnP(panel_coordinates, points, cam_matrix, dist, flags=cv.SOLVEPNP_ITERATIVE)
            cords.append([tvec, np.degrees(rvec)])
        return cords
    else:
        return []