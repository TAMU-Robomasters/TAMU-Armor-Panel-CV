
DEBUG = True
SHOW_ICON_FILTERS = False

ENEMY_COLOR = 'RED'

# cam params - SVPro global shutter camera
SOURCE = "USB_CAM" # 'REALSENSE' 'USB_CAM' or video path
#ZOOM_MODE = "10m" # TODO: determines what calibration preset to use "WIDE" "5m" "7m" "10m"

cam_width = 1920
cam_height = 1080
cam_fps = 90
cam_exposure = -8

# image processing
blue_thresh = (215, 240)
red_thresh = (215, 240)

# light detection
angle_diff_multiplier = 1
misalignment_multiplier = 1.25
expected_distance_multiplier = 0.5
height_ratio_multiplier = 1

angle_diff_thresh = 45
misalignment_thresh = 30
height_ratio_thresh = (0.5, 2.0)
score_thresh = 50

# icon detection
icon_adaptive_thresh = (101, -1)
icon_tolerance = 75

