import time
from frame_proccesing import *
from armor import *
from icon_detection import *
from PnP import *
from config import *
from draw import *
from video_source import *

video_source_init()

#main loop
while True:
    frame = get_frame()

    start_time = time.time()

    contours = frame_process(frame)
    lights = bounding_boxes(contours, frame)  # Renamed variable to avoid conflict
    if len(lights) > 1:
        try:
            pairs = pairing(lights)
            panels = []
            for pair in pairs:
                panel = armour_corners(pair)
                icon_detection(panel, frame)
                get_cord(panel)
                panels.append(panel)
                if DEBUG:
                   draw(panel, frame)
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
