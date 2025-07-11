import pyvirtualcam
import depthai as dai
import numpy as np

# code to start OAK webcams - run this file in a different terminal instance

# important settings
cam_resolution = (1080,720) #3/2
output_resolution = (640, 480) #4/3
exposure = 3000
iso = 500
focal_length = 5

pipeline = dai.Pipeline()
pipeline.setXLinkChunkSize(0)
cam = pipeline.create(dai.node.ColorCamera)
cam.setColorOrder(dai.ColorCameraProperties.ColorOrder.RGB)
cam.setResolution(dai.ColorCameraProperties.SensorResolution.THE_1080_P)
cam.setPreviewSize(cam_resolution)
cam.setFps(60)
cam.setInterleaved(False)
cam.setIspScale(2,3)
xout = pipeline.create(dai.node.XLinkOut)
xout.setStreamName("rgb")
print('configuring camera')
cam.initialControl.setManualExposure(exposure,iso)
cam.initialControl.setAutoFocusMode(dai.RawCameraControl.AutoFocusMode.OFF)
cam.initialControl.setManualFocus(focal_length)
cam.preview.link(xout.input)
# Connect to device and start pipeline
with dai.Device(pipeline) as device, pyvirtualcam.Camera(width=output_resolution[0], height=output_resolution[1], fps=60, print_fps=True) as uvc:
    qRgb = device.getOutputQueue(name="rgb", maxSize=4, blocking=False)
    print("UVC running")
    while True:
        frame = qRgb.get().getFrame()
        transposed_frame = np.transpose(frame, (1, 2, 0))
        cropped_img = transposed_frame[int((cam_resolution[1]-output_resolution[1])/2):int(((cam_resolution[1]-output_resolution[1])/2)+output_resolution[1]), int((cam_resolution[0]-output_resolution[0])/2):int(((cam_resolution[0]-output_resolution[0])/2)+output_resolution[0])]
        uvc.send(cropped_img)