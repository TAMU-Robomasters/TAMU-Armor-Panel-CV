import cv2 as cv
import numpy as np
import datetime as dt
import os
import tqdm
from subsystems.video_source import video_source_init, get_frame

shape, fps = video_source_init()
frame = np.zeros(shape, dtype=np.uint8)
date = dt.datetime.now()
f_date = date.strftime("%Y-%m-%d_%H:%M:%S")

FILE_NAME = f'assets/{shape[1]}x{shape[0]}_{fps}-fps_{f_date}.mp4'

frame_buffer = []
 
print("Press 'q' to stop recording\n")
while True:
    frame[:] = get_frame()
 
    # Save frame
    frame_buffer.append(frame.copy())
 
    # Display the frame
    cv.imshow("Frame", frame)
    if cv.waitKey(1) & 0xFF == ord('q'):
        break

cv.destroyAllWindows()
# Define the codec and create VideoWriter object
fourcc = cv.VideoWriter_fourcc(*"mp4v")
out = cv.VideoWriter(FILE_NAME, fourcc, fps, (shape[1], shape[0]))
for frame in tqdm.tqdm(frame_buffer,desc='Saving video', unit='frames'):
    out.write(frame)
# Release everything
out.release()

full_path = os.path.abspath(FILE_NAME)
print(f'Video stored at {full_path}')