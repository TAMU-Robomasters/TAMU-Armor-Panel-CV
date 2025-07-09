import cv2 as cv

cap = cv.VideoCapture(0)
scale_factor = 0.5
cap.set(cv.CAP_PROP_FPS, 30)  # Set the desired frame rate
while True:
    ret, frame = cap.read()
    if not ret:
        break  # End of video or error
    # Process 'frame' here
    resized_image = cv.resize(frame, None, fx=scale_factor, fy=scale_factor, interpolation=cv.INTER_AREA)
    cv.imshow('Video Frame', resized_image)  # Display the frame
    if cv.waitKey(100) & 0xFF == ord('q'):  # Wait for 'q' key to exit
        break