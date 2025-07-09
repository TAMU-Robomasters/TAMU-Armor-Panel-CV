import cv2 as cv
import numpy as np

# camera intrinsics
dist = np.array([(0.12047717, -0.14761262, -0.02169371, -0.01160076, 0.10168257)])

cam_matrix = np.array([(679.13732673, 0, 296.00769657),
                        (0, 680.60272338, 202.34619921),
                        (0, 0, 1)])

# panel dimensions in cm
panel_coordinates = np.array([
    [-12.3/2, 12.4/2, 0],
    [12.3/2, 12.4/2, 0],
    [12.3/2, -12.4/2, 0],
    [-12.3/2, -12.4/2, 0]
], dtype=np.float32)

hero_coordinates = np.array([
    [-21.8/2, 12.4/2, 0],
    [21.8/2, 12.4/2, 0],
    [21.8/2, -12.4/2, 0],
    [-21.8/2, -12.4/2, 0]
], dtype=np.float32)



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