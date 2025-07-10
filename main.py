import time
from subsystems.frame_proccesing import *
from subsystems.armor import *
from subsystems.icon_detection import *
from subsystems.PnP import *
from config import *
from subsystems.draw import *
from subsystems.video_source import *

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
                good_panel = icon_detection(panel, frame)
                if good_panel:
                    get_cord(panel)
                    panels.append(panel)
                else:
                    pairs.remove(pair)
            if DEBUG:
                for panel in panels:
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
    elapsed_time = (end_time - start_time)
    print(f"elapsed time: {elapsed_time * 1000:.4f} ms, fps: {1 / elapsed_time:.2f}")


    if cv.waitKey(70) & 0xFF == ord('q'):
        break
