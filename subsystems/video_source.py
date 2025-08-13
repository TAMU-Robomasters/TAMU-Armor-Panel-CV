import cv2 as cv
import numpy as np
import numpy.typing as npt
import pyrealsense2 as rs
from typing import Tuple

import config
from config import *

cap = None
pipeline = None

def video_source_init():
    """
    Will setup, webcam, realsense, or file source
    """
    global cap, pipeline, realsense_frame  # Declare global variables

    if SOURCE == "USB_CAM":
        cap = cv.VideoCapture(0)
        cap.set(cv.CAP_PROP_FRAME_WIDTH, cam_width)
        cap.set(cv.CAP_PROP_FRAME_HEIGHT, cam_height)
        cap.set(cv.CAP_PROP_FPS, cam_fps)
        cap.set(cv.CAP_PROP_EXPOSURE, cam_exposure)
    elif SOURCE == "REALSENSE":  # Changed if to elif for better logic flow
        pipeline = rs.pipeline()

        # Configure cams
        config = rs.config()
        

        
        config.enable_cam(rs.cam.color, cam_width, cam_height, rs.format.bgr8, cam_fps)
        # config.enable_cam(rs.cam.depth, 640, 480, rs.format.z16, 30)

        # Start caming
        prof = pipeline.start(config)

        s = prof.get_device().query_sensors()[1]
        s.set_option(rs.option.exposure, 40)
        
        # for optimization
        return ((cam_height, cam_width, 3), cam_fps)
    else:
        cap = cv.VideoCapture(SOURCE)


def get_frame():   
    if SOURCE != "REALSENSE":
        ret, frame = cap.read()
        if not ret:
            return None
        return frame
    else:
        return pipeline.wait_for_frames().get_color_frame().get_data()

# return dist coef and cam mat
def get_intrinsics() -> Tuple[npt.NDArray[np.float32]]:  
    if SOURCE == "USB_CAM":
        distortion_matrix = np.load('calibration/presets/dist.pkl', allow_pickle=True)
        camera_matrix = np.load('calibration/presets/cameraMatrix.pkl', allow_pickle=True)
        return distortion_matrix, camera_matrix
    
    elif SOURCE == "REALSENSE":
        ctx = rs.context()
        devices = ctx.query_devices()
        if len(devices) == 0:
            raise RuntimeError("No RealSense device connected")
        dev = devices[0]

        try:
            color_sensor = dev.query_sensors()[1]
        except Exception as e:
            raise RuntimeError("Color sensor not found")

        try:
            vsp = color_sensor.get_cam_profiles()[0].as_video_cam_profile()
        except Exception as e:
            raise RuntimeError("Video cam profile not found")

        intr = vsp.get_intrinsics()

        # camera intrinsics
        dist = np.array(intr.coeffs)

        cam_matrix = np.array([[intr.fx, 0, intr.ppx],
                               [0, intr.fy, intr.ppy],
                               [0, 0, 1]])
        
        return dist, cam_matrix
    
    else:
        # raise RuntimeError("Please implement camera's get intrinsics function")
        return config.distortion_matrix, config.cam_matrix