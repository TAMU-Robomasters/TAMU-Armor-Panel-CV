import cv2 as cv
import time
import numpy as np
import math

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
        _, thresh = cv.threshold(b, 225, 240, cv.THRESH_BINARY) # tune before match
    elif (enemy_color == 'RED'):
        _, thresh = cv.threshold(r, 225, 240, cv.THRESH_BINARY) # tune before match
    else:
        print('invalid color')

    kernel = np.ones((5,5),np.uint8)
    closing = cv.morphologyEx(thresh, cv.MORPH_CLOSE, kernel)



    boxes = []

    contours, _ = cv.findContours(closing, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
    for cnt in contours:
        rect = cv.minAreaRect(cnt)  # ((cx, cy), (width, height), angle)
        hbad, wbad = rect[1]
        if rect[1][0] > rect[1][1]:
            h,w = rect[1]
        else:
            w,h = rect[1]
        area = w*h
        
        angle = rect[2]
        if wbad > hbad:
            angle += 90
        
        #print(angle-90)

        if ((abs(angle-90) > 45) or (area < 150)):
            continue
        else:
            box = cv.boxPoints(rect)    # Get 4 corner points of the rotated box
            box = np.intp(box)           # Convert to integer for drawing
            cv.drawContours(frame, [box], 0, (0, 255, 0), 2)
            boxes.append({'cx':rect[0][0], 'cy':rect[0][1], "width":w, "height" : h, "angle":angle})

    #boxes.sort(key=lambda L: L[0])
    pairs = []
    

    # uses scores to evelutae possible pairs
    #good fucking luck bebugging idiot
    # i dont even know what the fuck i did
    # 🪿
    # -Jai(July 2025)
    if len(boxes) > 1:
        for i in range(len(boxes)):
            if i < len(boxes) or boxes[i] == None:
                scores = []
                for j in range(len(boxes)):
                    if j != i and i < len(boxes) and boxes[j] != None:
                        try:
                            light1 = boxes[i]
                            light2 = boxes[j]
                            angle_diff = abs(light1["angle"] - light2["angle"])
                            misalignment_angle = abs(math.degrees((np.atan((light1["cy"] - light2["cy"])/ (light1["cx"] - light2["cx"])))))
                            average_height = (light1["height"] + light2["height"]) / 2
                            distance = math.sqrt((light1["cx"] - light2["cx"]) ** 2 + (light1["cy"] - light2["cy"]) ** 2)
                            expected_distance = abs((average_height / (5.5/13)) - distance)
                            hr = light1["height"] / light2["height"]

                            score = angle_diff + misalignment_angle + expected_distance + hr
                            scores.append(score)
                        except:
                            pass
                try:
                    if min(scores) < 50:
                        minimum_score_index = scores.index(min(scores))
                        pairs.append([box[i], box[i+1+minimum_score_index]]) 
                        boxes[minimum_score_index] = None
                except:
                    pass
            
            boxes[i] = None
                #print(f"{score} = {angle_diff} + {misalignment_angle} + {expected_distance} + {hr}")
    
    print(pairs)





        


    # except:
    #      print('doodoo')
    
    cv.imshow('View', frame)


    end_time = time.time()
    elapsed_time = (end_time - start_time) * 1000.0
    #print(f"elapsed time: {elapsed_time:.4f} ms")


    if cv.waitKey(1) & 0xFF == ord('q'):
        break