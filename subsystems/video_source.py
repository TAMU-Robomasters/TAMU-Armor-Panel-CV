import cv2 as cv
import numpy as np
import pyrealsense2 as rs
from config import SOURCE

cap = None
pipeline = None

def video_source_init():
    """
    Will setup, webcam, realsense, or file source
    """
    global cap, pipeline  # Declare global variables
    
    if SOURCE == "USB_CAM":
        cap = cv.VideoCapture(0)
    elif SOURCE == "REALSENSE":  # Changed if to elif for better logic flow
        pipeline = rs.pipeline()

        # Configure streams
        config = rs.config()
        config.enable_stream(rs.stream.color, 1920, 1080, rs.format.bgr8, 30)
        # config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)

        # Start streaming
        prof = pipeline.start(config)

        s = prof.get_device().query_sensors()[1]
        s.set_option(rs.option.exposure, 40)
    else:
        cap = cv.VideoCapture(SOURCE)

def get_frame():
    if SOURCE != "REALSENSE":
        ret, frame = cap.read()
        cv.imshow("frame", frame)
        if not ret:
            return None
        return frame
    else:
        frames = pipeline.wait_for_frames()
        color_frame = frames.get_color_frame()
        frame = np.asanyarray(color_frame.get_data())
        return frame