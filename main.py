import cv2 as cv
import numpy as np
import time
from frame_proccesing import *
from armor import *
from icon_detection import *
from PnP import *
from config import *
import pyrealsense2 as rs

try:
    # Create a context object. This object owns the handles to all connected realsense devices
    pipeline = rs.pipeline()

    # Configure streams
    config = rs.config()
    config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)

    # Start streaming
    pipeline.start(config)
except:
    pass



#main loop
while True:
    frame = pipeline.wait_for_frames()
    print(type(frame))

    # if not ret:
    #     print("frame capture fail")
    #     break

    start_time = time.time()

    contours = frame_process(frame)
    detected_boxes = bounding_boxes(contours, frame)  # Renamed variable to avoid conflict
    if len(detected_boxes) > 1:
        try:
            pairs = pair(detected_boxes, frame)
            panels = armour_corners(pairs, frame)
            ids = icon_detection(panels, frame)
            cords = get_cord(panels, frame)
        except Exception as e:
            print(f"Error in get_cord: {e}")
            cords = []
    else:
        cords = []

    if DEBUG:
        #print(cords)

        # time logging
        cv.imshow("frame", frame)
    end_time = time.time()
    elapsed_time = (end_time - start_time) * 1000.0
    print(f"elapsed time: {elapsed_time:.4f} ms")


    if cv.waitKey(1) & 0xFF == ord('q'):
        break