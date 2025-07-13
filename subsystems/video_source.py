import cv2 as cv
import numpy as np
import numpy.typing as npt
import pyrealsense2 as rs
from typing import Tuple

import config
from config import SOURCE

cap = None
pipeline = None



def video_source_init():
    """
    Will setup, webcam, realsense, or file source
    """
    global cap, pipeline, realsense_frame  # Declare global variables
    
    if SOURCE == "USB_CAM":
        cap = cv.VideoCapture(0)
    elif SOURCE == "REALSENSE":  # Changed if to elif for better logic flow
        pipeline = rs.pipeline()

        # Configure streams
        config = rs.config()
        
        # width = 640
        # height = 480
        # fps = 60
        
        width = 1920
        height = 1080
        fps = 30
        
        config.enable_stream(rs.stream.color, width, height, rs.format.bgr8, fps)
        # config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)

        # Start streaming
        prof = pipeline.start(config)

        s = prof.get_device().query_sensors()[1]
        s.set_option(rs.option.exposure, 40)
        
        # for optimization
        return ((height, width, 3), fps)
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
        dist = config.dist
        cam_matrix = config.cam_matrix
        return dist, cam_matrix
    
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
            vsp = color_sensor.get_stream_profiles()[0].as_video_stream_profile()
        except Exception as e:
            raise RuntimeError("Video stream profile not found")

        intr = vsp.get_intrinsics()

        # camera intrinsics
        dist = np.array(intr.coeffs)

        cam_matrix = np.array([[intr.fx, 0, intr.ppx],
                               [0, intr.fy, intr.ppy],
                               [0, 0, 1]])
        
        return dist, cam_matrix
    
    else:
        # raise RuntimeError("Please implement camera's get intrinsics function")
        dist = np.array([(0.12047717, -0.14761262, -0.02169371, -0.01160076, 0.10168257)])

        cam_matrix = np.array([(679.13732673, 0, 296.00769657),
                               (0, 680.60272338, 202.34619921),
                               (0, 0, 1)])
        return dist, cam_matrix