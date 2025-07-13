import numpy as np

DEBUG = True

ENEMY_COLOR = 'RED'
SOURCE = "USB_CAM" # 'REALSENSE' 'USB_CAM' or video path

# cam params - change them to the correct camera's
dist = np.array([(0.12047717, -0.14761262, -0.02169371, -0.01160076, 0.10168257)])

cam_matrix = np.array([(679.13732673, 0, 296.00769657),
                        (0, 680.60272338, 202.34619921),
                        (0, 0, 1)])
