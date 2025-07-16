import cv2 as cv
import numpy as np
import config
from subsystems.video_source import get_intrinsics

# camera intrinsics
dist, cam_matrix = get_intrinsics()

# panel dimensions in cm from config
panel_coordinates = config.panel_coordinates
hero_coordinates = config.hero_coordinates


def get_cord(panel):
    """
    Use PnP to find tvec and rvec of panels
    :param list_of_points: List of points in image coordinates
    :return: [[tvec, rvec], ...]
    """
    if panel:
        points = panel.corners
        # Convert points to the correct format
        points = np.array(points, dtype=np.float32).reshape(-1, 2)

        # Ensure we have exactly 4 points
        if points.shape[0] != 4:
            pass
        if panel.id != 0:
            success, rvec, tvec = cv.solvePnP(
                panel_coordinates,
                points,
                cam_matrix,
                dist,
                flags=cv.SOLVEPNP_ITERATIVE
            )
        else:
            success, rvec, tvec = cv.solvePnP(
                hero_coordinates,
                points,
                cam_matrix,
                dist,
                flags=cv.SOLVEPNP_ITERATIVE
            )

        if success:
            panel.tvec = tvec
            panel.rvec = rvec