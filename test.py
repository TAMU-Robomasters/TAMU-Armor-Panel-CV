import cv2 as cv

camera = cv.VideoCapture(0)


while True:
    _, frame = camera.read()

    cv.imshow("frame", frame)

    cv.waitKey(0)
    cv.destroyAllWindows()