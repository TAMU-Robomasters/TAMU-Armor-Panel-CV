import cv2 as cv
import time
import numpy as np
import math
import os

enemy_color = 'RED' # 'BLUE' or 'RED'

armor_height_ratio = 12.5/6

folder_path = "TAMU-Armor-Panel-CV\\icons"

icon_list = []
for pic in os.listdir(folder_path):
    full_path = os.path.join(folder_path, pic)
    picture = cv.imread(full_path)
    gray = cv.cvtColor(picture, cv.COLOR_BGR2GRAY)
    icon_list.append(gray)


# camera intrinsics
dist = np.array([(0.12047717, -0.14761262, -0.02169371, -0.01160076, 0.10168257)])

cam_matrix = np.array([(679.13732673, 0, 296.00769657),
                        (0, 680.60272338, 202.34619921),
                        (0, 0, 1)])

# panel dimensions in cm
panel_coordinates = np.array([
    [-12.3/2, 12.4/2, 0],
    [12.3/2, 12.4/2, 0],
    [12.3/2, -12.4/2, 0],
    [-12.3/2, -12.4/2, 0]
], dtype=np.float32)



# bind and start webcam - cameras with less FOV and more zoom are better for more consistent long-distance detection.
camera = cv.VideoCapture(0)
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
        _, thresh = cv.threshold(b, 215, 240, cv.THRESH_BINARY) # tune before match
    elif (enemy_color == 'RED'):
        _, thresh = cv.threshold(r, 215, 240, cv.THRESH_BINARY) # tune before match
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

        if ((abs(angle-90) > 45)):
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
                    if min(scores) < 70:
                        minimum_score_index = scores.index(min(scores))
                        pairs.append([boxes[i], boxes[i+1+minimum_score_index]]) 
                        boxes[minimum_score_index] = None
                except:
                    pass
            
            boxes[i] = None
                #print(f"{score} = {angle_diff} + {misalignment_angle} + {expected_distance} + {hr}")

    #                 first box              second box
    # pairs = [[cx, cy, w, h, angle],[cx, cy, w, h, angle]]
    for pair in pairs:
        if (pair[0]["cx"] <= pair[1]["cx"]):
            left = pair[0]
            right = pair[1]
        else:
            left = pair[1]
            right = pair[0]

        # 
        top_left = [int(left["cx"] + left["width"]*0.5 - (left["height"] * armor_height_ratio)*0.5 * math.cos(math.radians(left["angle"]))), int((left["cy"] - ((left["height"] * armor_height_ratio)*0.5 * math.sin(math.radians(left["angle"])))))]
        top_right = [int(right["cx"] - right["width"]*0.5 - (right["height"] * armor_height_ratio)*0.5 * math.cos(math.radians(right["angle"]))), int((right["cy"] - ((right["height"] * armor_height_ratio)*0.5 * math.sin(math.radians(right["angle"])))))]
        bottom_left = [int(left["cx"] + left["width"]*0.5 + (left["height"] * armor_height_ratio)*0.5 * math.cos(math.radians(left["angle"]))), int((left["cy"] + ((left["height"] * armor_height_ratio)*0.5 * math.sin(math.radians(left["angle"])))))]
        bottom_right = [int(right["cx"] - right["width"]*0.5 + (right["height"] * armor_height_ratio)*0.5 * math.cos(math.radians(right["angle"]))), int((right["cy"] + ((right["height"] * armor_height_ratio)*0.5 * math.sin(math.radians(right["angle"])))))]

        points = np.array([top_left,top_right,bottom_right,bottom_left], dtype=np.int32)
        points = points.reshape((-1,1,2))

        


        cv.polylines(frame, [points], True, (255,255,255), 2)

        expected_points = np.float32([[0,0],[300,0],[300,300],[0,300]])

        points = np.float32(points)

        M = cv.getPerspectiveTransform(points,expected_points)

        warpped = cv.warpPerspective(frame, M, (300,300))

        warpped = cv.cvtColor(warpped, cv.COLOR_BGR2GRAY)

        adaptive_tresh = cv.adaptiveThreshold(warpped, 255, cv.ADAPTIVE_THRESH_MEAN_C, cv.THRESH_BINARY, 41, -6)

        icon_contours, _ = cv.findContours(adaptive_tresh, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)

        # find the biggest countour (c) by the area
        try:
            c = max(icon_contours[2:], key = cv.contourArea)
        except:
            pass

        # draw the biggest contour (c) in green
        x,y,w,h = cv.boundingRect(c)
        cv.rectangle(adaptive_tresh,(x,y),(x+w,y+h),(255,255,255),2)
        cropped = adaptive_tresh[y:y+h, x:x+w]
        resized = cv.resize(cropped, (300,300))

        icon_scores = []
        for pic in icon_list:
            compared = cv.bitwise_xor(pic, resized)
            icon_scores.append(int(100 * (1-(np.sum(compared == 255) / 300**2))))
            cv.imshow("compared", compared)
        # 0 - 1, 1 - 3, 2 - sentry
        id = icon_scores.index(max(icon_scores))

        if(id == 0):
            str_holder = "1"
        elif(id == 1):
            str_holder = "3"
        else:
            str_holder = "Sentry"
        cv.putText(frame, str_holder, tuple(top_left), cv.FONT_HERSHEY_SIMPLEX, 3, (255,0,0), 2)

        success, rvec, tvec = cv.solvePnP(panel_coordinates, points, cam_matrix, dist, flags=cv.SOLVEPNP_ITERATIVE)
        print(np.degrees(rvec))
    
    cv.imshow('View', frame)




    end_time = time.time()
    elapsed_time = (end_time - start_time) * 1000.0
    #print(f"elapsed time: {elapsed_time:.4f} ms")


    if cv.waitKey(1) & 0xFF == ord('q'):
        break