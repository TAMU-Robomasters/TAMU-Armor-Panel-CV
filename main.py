import cv2 as cv
import time
import numpy as np

enemy_color = 'RED' # 'BLUE' or 'RED'

# bind and start webcam - cameras with less FOV and more zoom are better for more consistent long-distance detection.
camera = cv.VideoCapture(0, cv.CAP_DSHOW)

# configure cam
camera.set(cv.CAP_PROP_FRAME_WIDTH, 640)
camera.set(cv.CAP_PROP_FRAME_HEIGHT, 480)
camera.set(cv.CAP_PROP_AUTOFOCUS, 0)
camera.set(cv.CAP_PROP_AUTOFOCUS, 100) # 50 ft or something idk
camera.set(cv.CAP_PROP_AUTO_EXPOSURE, 0.25)
camera.set(cv.CAP_PROP_EXPOSURE, -9.0) # tune before match
#camera.set(cv.CAP_PROP_FPS, 100) # not sure if this does anything

# def gamma_trans(img, gamma):
#     gamma_table=[np.power(x/255.0,gamma)*255.0 for x in range(256)]
#     gamma_table=np.round(np.array(gamma_table)).astype(np.uint8)
#     return cv.LUT(img,gamma_table)

if not camera.isOpened():
    print("camera error")
    exit()

# frame loop - all processing is done in here
while True:
    ret, frame = camera.read()
    #ret, frame =cv.imread(path, flag)

    if not ret:
        print("frame capture fail")
        break

    start_time = time.time()
    
    # get frame color channels
    b,g,r = cv.split(frame)

    

    # thresh the correct color channel
    if (enemy_color == 'BLUE'):
        _, thresh = cv.threshold(b, 230, 240, cv.THRESH_BINARY) # tune before match
    elif (enemy_color == 'RED'):
        _, thresh = cv.threshold(r, 230, 240, cv.THRESH_BINARY) # tune before match
    else:
        print('invalid color')

    contours, _ = cv.findContours(thresh, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
    for cnt in contours:
        rect = cv.minAreaRect(cnt)  # ((cx, cy), (width, height), angle)
        box = cv.boxPoints(rect)    # Get 4 corner points of the rotated box
        box = np.intp(box)           # Convert to integer for drawing
        cv.drawContours(frame, [box], 0, (0, 255, 0), 2)
        angle = rect[2]
        w, h = rect[1]
        if w < h:
            angle -= 90
        
        # print(angle)

    # except:
    #      print('doodoo')
    
    cv.imshow('View', frame)


    end_time = time.time()
    elapsed_time = (end_time - start_time) * 1000.0
    print(f"elapsed time: {elapsed_time:.4f} ms")


    if cv.waitKey(1) & 0xFF == ord('q'):
        break