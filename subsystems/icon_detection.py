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
    points = np.float32(panel.corners)
    M = cv.getPerspectiveTransform(points, expected_points)
    warped = cv.warpPerspective(frame, M, (300, 300))
    warped = cv.cvtColor(warped, cv.COLOR_BGR2GRAY)

    adaptive_thresh = cv.adaptiveThreshold(warped, 255, cv.ADAPTIVE_THRESH_MEAN_C,
                                         cv.THRESH_BINARY, 101, -1)

    icon_contours, _ = cv.findContours(adaptive_thresh, cv.RETR_TREE,
                                     cv.CHAIN_APPROX_SIMPLE)

    try:
        # Find largest contour after first two
        c = max(icon_contours[2:], key=cv.contourArea)
        x, y, w, h = cv.boundingRect(c)

        # Crop and resize in one step
        cropped = cv.resize(adaptive_thresh[y:y+h, x:x+w], (300, 300))

        # Vectorized comparison with all icons at once
        # Stack all icons into a 3D array (n_icons x height x width)
        icon_stack = np.stack(icon_list)

        # Broadcast cropped image to same shape as icon_stack
        # and compute XOR for all icons simultaneously
        compared = np.bitwise_xor(icon_stack, cropped)

        # Compute mean intensity for all icons at once
        icon_scores = np.mean(compared, axis=(1, 2))

        if DEBUG:
            for i, comp in enumerate(compared):
                cv.imshow(f"icon + {i}", comp)

        min_score = np.min(icon_scores)
        if min_score > 100:
            return False

        panel.id = np.argmin(icon_scores)
        return True

    except Exception:
        return False