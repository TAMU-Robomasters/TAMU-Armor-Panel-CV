from dataclasses import dataclass, field
import math
import time
import cv2
import numpy as np
import numpy.typing as npt
from typing import Tuple, Optional, List
from threading import Lock
from robomaster_particle_filters import fast_plate_orbit

import cv2 as cv
import numpy as np
import time
from frame_proccesing import *
from armor import *
from icon_detection import *
from PnP import *
from config import *
import pyrealsense2 as rs
from draw import *


ANGULAR_VELOCITY_STEP_SIZE = 2.0
POSITION_DIAGONAL_COVARIANCE = np.array([0.0001, 0.0001, 0.0001])
RADIAL_OFFSETS = [0.0, 0.0, 0.0, 0.0]
Z_OFFSETS = [0.0, 0.007, 0.0, 0.007]
VISIBILITY_ANGLE_THRESHOLD = math.pi / 3.0




@dataclass
class SimulatedRobotState:
    radius: float
    angle: float
    angular_velocity: float
    center: npt.NDArray[np.float64]
    observer: npt.NDArray[np.float64]

    visible_plates: List[npt.NDArray[np.float64]] = field(default_factory=list)

    def plate_positions(self) -> List[npt.NDArray[np.float64]]:
        offsets = [(0) * math.pi, (1 / 2) * math.pi,
                   (1) * math.pi, (3 / 2) * math.pi]

        def to_plate(offset, radial_offset, z_offset):
            horizontal_displacement = np.array(
                [math.cos(self.angle + offset), math.sin(self.angle + offset), 0.0])
            vertical_displacement = np.array([0.0, 0.0, z_offset])
            return self.center + (self.radius + radial_offset) * horizontal_displacement + vertical_displacement

        return [to_plate(*args) for args in zip(offsets, RADIAL_OFFSETS, Z_OFFSETS)]

    def set_visible_plate_positions(self, plates: List[npt.NDArray[np.float64]]):
        plates = [plate / 20.0 for plate in plates]
        print(plates)
        self.visible_plates = plates

    def visible_plate_positions(self) -> List[npt.NDArray[np.float64]]:
        return self.visible_plates

    def step_up_velocity(self):
        self.angular_velocity += ANGULAR_VELOCITY_STEP_SIZE

    def step_down_velocity(self):
        self.angular_velocity -= ANGULAR_VELOCITY_STEP_SIZE

    def update(self, offset_seconds: float):
        self.angle += offset_seconds * self.angular_velocity

    def set_center(self, center: npt.NDArray[np.float64]):
        self.center = center

    def set_observer(self, observer: npt.NDArray[np.float64]):
        self.observer = observer


class InteractiveFastPlateOrbitFilterDemo:
    window_title: str
    h: int
    w: int
    simulated_robot_state: SimulatedRobotState
    number_of_particles: int
    particle_filter_configuration: fast_plate_orbit.ParticleFilterConfigurationParameters
    input_image: npt.NDArray[np.uint8]
    filter_lock: Lock
    latest_update_time: Optional[float]
    filter: Optional[fast_plate_orbit.ParticleFilter]

    def __init__(self, window_title: str, resolution: Tuple[int, int], simulated_robot_state: SimulatedRobotState, number_of_particles: int, config: fast_plate_orbit.ParticleFilterConfigurationParameters):
        self.window_title = window_title
        self.h, self.w = resolution
        self.simulated_robot_state = simulated_robot_state
        self.number_of_particles = number_of_particles
        self.particle_filter_configuration = config
        self.input_image = np.zeros((self.h, self.w, 3), np.uint8)
        self.state_lock = Lock()
        self.latest_update_time = None
        self.filter = None
        self.reset = False
        cv2.namedWindow(window_title, cv2.WINDOW_NORMAL)
        cv2.imshow(window_title, self.input_image)
        cv2.setMouseCallback(window_title, self.on_mouse)

    def _get_observation(self) -> fast_plate_orbit.Observation:
        plates = self.simulated_robot_state.visible_plate_positions()
        assert len(plates) == 1 or len(plates) == 2
        if len(plates) == 1:
            plate_one, = plates
            observation = fast_plate_orbit.Observation.from_one_plate(
                self.simulated_robot_state.observer,
                fast_plate_orbit.ObservedPlate(
                    plate_one, POSITION_DIAGONAL_COVARIANCE),
            )
        elif len(plates) == 2:
            plate_one, plate_two = plates
            observation = fast_plate_orbit.Observation.from_two_plates(
                self.simulated_robot_state.observer,
                fast_plate_orbit.ObservedPlate(
                    plate_one, POSITION_DIAGONAL_COVARIANCE),
                fast_plate_orbit.ObservedPlate(
                    plate_two, POSITION_DIAGONAL_COVARIANCE),
            )
        return observation

    def initalize_filter(self):
        observation = self._get_observation()
        self.filter = fast_plate_orbit.ParticleFilter(
            self.number_of_particles, observation, self.particle_filter_configuration)
        self.latest_update_time = time.monotonic()

    def update_filter(self) -> fast_plate_orbit.Prediction:
        current_time = time.monotonic()
        elapsed = current_time - self.latest_update_time
        self.simulated_robot_state.update(elapsed)
        observation = self._get_observation()
        self.filter.update_state_with_observation(elapsed, observation)
        self.latest_update_time = current_time
        return self.filter.extrapolate_state(0.0)

    def on_mouse(self, event, x: int, y: int, flags, param):
        pass
        
    def update_plates(self, plates: List[npt.NDArray[np.float64]]):
        with self.state_lock:
            if self.filter is not None and self.latest_update_time is not None:
                self.simulated_robot_state.set_visible_plate_positions(plates)
                _ = self.update_filter()
            else:
                self.simulated_robot_state.set_visible_plate_positions(plates)
                self.initalize_filter()


if __name__ == "__main__":
    config = fast_plate_orbit.ParticleFilterConfigurationParameters(
        0.11, 2.0, 0.001, 0.005, 0.0001, 6, 2.5, 3.0, np.array([6.0, 6.0]), np.array([10.0, 10.0]))
    simulated_robot_state = SimulatedRobotState(
        radius=0.1, angle=0.0, angular_velocity=0.0, center=np.zeros(3), observer=np.zeros(3))
    demo = InteractiveFastPlateOrbitFilterDemo(window_title="demo", resolution=(
        1024, 1024), simulated_robot_state=simulated_robot_state, number_of_particles=(1000000), config=config)

    

RED = (0, 0, 255)
BLUE = (255, 0, 0)
GREEN = (0, 255, 0)
WHITE = (255, 255, 255)
CYAN = (255, 255, 0)
SPACE_KEY = 32
demo.update_plates([np.array([1,1,0],dtype=np.float64)])

#your mom
# Create a context object. This object owns the handles to all connected realsense devices
pipeline = rs.pipeline()

# Configure streams
config = rs.config()
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 60)
#config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)

# Start streaming
prof = pipeline.start(config)


s = prof.get_device().query_sensors()[1]
s.set_option(rs.option.exposure, 40)

#main

while True:

    frames = pipeline.wait_for_frames()

    color_frame = frames.get_color_frame()

    frame = np.asanyarray(color_frame.get_data())

    # if not ret:
    #     print("frame capture fail")
    #     break

    start_time = time.time()
    panels = []

    contours = frame_process(frame)
    lights = bounding_boxes(contours, frame)  # Renamed variable to avoid conflict
    if len(lights) > 1:
        try:
            pairs = pairing(lights)
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
        # print(cords)

        # time logging
        cv.imshow("frame", frame)
    end_time = time.time()
    elapsed_time = (end_time - start_time) * 1000.0
    print(f"elapsed time: {elapsed_time:.4f} ms")

    if demo.filter is not None and demo.latest_update_time is not None:
        print([np.array([panel.tvec[0],panel.tvec[2],panel.tvec[1]],dtype=np.float64) for panel in panels])
        plates = []
        if plates != []:
            demo.update_plates(plates)
        with demo.state_lock:
            prediction = demo.update_filter()

        demo.input_image = np.zeros((demo.h, demo.w, 3), np.uint8)

        for plate in prediction.predicted_plates():
            x, y, _ = plate.position()
            v_x, v_y, _ = plate.velocity()
            center = int(demo.w * x), int(demo.h * y)
            end = int(demo.w * (x + 0.5 * v_x)
                        ), int(demo.h * (y + 0.5 * v_y))
            cv2.arrowedLine(demo.input_image, center,
                            end, color=GREEN, thickness=5)
            cv2.circle(demo.input_image, center,
                        radius=2, color=GREEN, thickness=1)
        
        x, y, z = prediction.center()                
        v_x, v_y = prediction.center_velocity()
        center = int(demo.w * x), int(demo.h * y)
        end = int(demo.w * (x + 0.5 * v_x)
                    ), int(demo.h * (y + 0.5 * v_y))
        radii = int(demo.w * prediction.radius()), int(demo.h * prediction.radius())
        
        degrees = (180.0 / math.pi) * prediction.orientation()
        cv2.ellipse(demo.input_image, center, radii, degrees,
                    0.0, 360.0, color=WHITE, thickness=3)
        cv2.circle(demo.input_image, center, radius=8,
                    color=WHITE, thickness=-1)
        cv2.arrowedLine(demo.input_image, center,
                        end, color=WHITE, thickness=5)

        for plate in demo.simulated_robot_state.visible_plate_positions():
            x, y, _ = plate
            center = int(demo.w * x), int(demo.h * y)
            cv2.circle(demo.input_image, center,
                        radius=8, color=BLUE, thickness=-1)

        x, y, _ = demo.simulated_robot_state.observer
        center = int(demo.w * x), int(demo.h * y)
        cv2.circle(demo.input_image, center,
                    radius=100, color=CYAN, thickness=-1)

    cv2.imshow(demo.window_title, demo.input_image)

    key = cv2.waitKey(1)
    if key == SPACE_KEY:
        demo.input_image = np.zeros((demo.h, demo.w, 3), np.uint8)

        demo.input_image[:, :] = np.array(RED)
        cv2.imshow(demo.window_title, demo.input_image)
        _ = cv2.waitKey(200)

        with demo.state_lock:
            demo.initalize_filter()
        _ = cv2.waitKey(16)

