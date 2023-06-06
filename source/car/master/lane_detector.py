import numpy as np
import cv2
from multiprocessing import Process
import threading
import time
from picamera2 import Picamera2
from image_processor import ImageProcessor
from camera import Camera
from slave import Slave
from steering_controller import SteeringController

class LaneDetector:
    def __init__(self, n_windows, window_width):
        self.n_windows = n_windows
        self.window_width = window_width
        self.lane_fit = [False, False]
        self.lane_points = [None, None]
        self.center_x_points = []
        self.center_y_points = []
        
    def find_lanes(self, frame, draw_frame):
        if self.lane_fit[0] and self.lane_fit[1]:
            pass
        elif self.lane_fit[0] and not self.lane_fit[1]:
            pass
        elif not self.lane_fit[0] and self.lane_fit[1]:
            pass
        else:
            x_0_points, y_0_points = self.find_lane_from_start(frame, draw_frame, color=(0,255,0))
            #self.black_out_lane(frame, x_0_points, y_0_points)
            if len(x_0_points) >= 5:
                self.lane_points[0] = (x_0_points, y_0_points)
            else:
                self.lane_points[0] = None
            
            x_1_points, y_1_points = self.find_lane_from_start(frame, draw_frame, color=(255,0,0))
            #self.black_out_lane(frame, x_1_points, y_1_points)
            if len(x_1_points) >= 5:
                self.lane_points[1] = (x_1_points, y_1_points)
            else:
                self.lane_points[1] = None
        
    def get_lane_data(self, frame):
        if not all(self.lane_points): return None
        position_error = self.center_x_points[0] - frame.shape[1]//2
        angle = -np.arctan2(self.center_y_points[4]-self.center_y_points[0], self.center_x_points[4]-self.center_x_points[0]) * 180 / np.pi
        angle_error = 90 - angle
        
        longest_lane_x, longest_lane_y = self.lane_points[0] if len(self.lane_points[0][0]) >= len(self.lane_points[1][0]) else self.lane_points[1]
        
        first_derivative = []
        for i in range(len(longest_lane_x)-1):
            first_derivative.append((longest_lane_x[i+1] - longest_lane_x[i]) / (longest_lane_y[i+1] - longest_lane_y[i]))
            
        second_derivative = []
        for i in range(len(first_derivative)-1):
            second_derivative.append(abs((first_derivative[i+1] - first_derivative[i]) / (longest_lane_y[i+1] - longest_lane_y[i])))
        curvature_factor = np.max(np.array(second_derivative))        
        return position_error, angle_error, curvature_factor
    
    def find_lanes_center(self, draw_frame):
        if not all(self.lane_points): return [], []
        
        x_0_points, y_0_points = self.lane_points[0]
        x_1_points, y_1_points = self.lane_points[1]
        
        self.center_x_points, self.center_y_points = [], []
        for i in range(min(len(x_0_points), len(x_1_points))):
            #distances = np.sqrt(np.power(x_1_points-x_1_points[i], 2) + np.power(y_2_points-y_1_points[i], 2))
            #closest_point = np.argmin(distances)
            #x_center = np.mean([x_1_points[i], x_2_points[closest_point]]).astype(int)
            #y_center = np.mean([y_1_points[i], y_2_points[closest_point]]).astype(int)
            
            x_center = np.mean(np.array([x_0_points[i], x_1_points[i]])).astype(int)
            y_center = np.mean(np.array([y_0_points[i], y_1_points[i]])).astype(int)
            
            self.center_x_points.append(x_center)
            self.center_y_points.append(y_center)
            cv2.circle(draw_frame, (x_center, y_center), 3, (0,255,255), -1)
            
    def find_lane_from_points(self, frame, draw_frame):
        pass
    
    def find_lane_from_start(self, frame, draw_frame, color=(0,255,0)):
        start = self.find_lane_start(frame)
        if start is None: return [], []
        lane_x_points, lane_y_points = self.window_search(frame, draw_frame, start[0], color)
        return lane_x_points, lane_y_points
    
    def find_lane_start(self, frame):
        reversed_frame = np.flipud(frame)
        nonzero_indices = np.nonzero(reversed_frame)
        if len(nonzero_indices[0]) > 0:
            return nonzero_indices[1][0], (frame.shape[0]-1) - nonzero_indices[0][0]
        return None
        
    def window_search(self, frame, draw_frame, start, color=(0,255,0)):
        window_height = int(frame.shape[0]/self.n_windows)
        min_pixels = 20
        curr_x = start
        
        nonzero = frame.nonzero()
        nonzero_y = np.array(nonzero[0])
        nonzero_x = np.array(nonzero[1])
        
        lane_x_points = []
        lane_y_points = []
        offset = 0
        bad_windows = 0
        for window in range(self.n_windows):
            curr_x  += offset 
            left = int(curr_x - (self.window_width/2))
            right = int(curr_x + (self.window_width/2))
            upper = int(frame.shape[0] - (window+1)*window_height)
            lower = int(frame.shape[0] - window*window_height)
            
        
            window_points = ((nonzero_y >= upper) & (nonzero_y < lower) & (nonzero_x >= left) & (nonzero_x < right)).nonzero()[0]
            if len(window_points) > min_pixels:
                bad_windows = 0
                curr_y = int(upper + (lower-upper)/2)
                curr_x = np.int(np.mean(nonzero_x[window_points]))
                if lane_x_points: offset = curr_x - lane_x_points[-1]
                
                lane_x_points.append(curr_x)
                lane_y_points.append(curr_y)
                cv2.circle(draw_frame, (curr_x, curr_y), 3, (0,0,255), -1)
            else:
                bad_windows += 1
                if bad_windows > 3: break
                    
            cv2.rectangle(draw_frame, (left, upper), (right, lower), color=color, thickness=1)
            cv2.rectangle(frame, (left, upper), (right, lower), color=(0,0,0), thickness=-1)
        return np.array(lane_x_points), np.array(lane_y_points)
    
    def black_out_lane(self, frame, x_points, y_points):
        window_height = int(frame.shape[0]/self.n_windows)
        for i in range(len(x_points)):
            left = x_points[i] - int(self.window_width/2)
            right = x_points[i] + int(self.window_width/2)
            upper = y_points[i] - int(window_height/2)
            lower = y_points[i] + int(window_height/2)
            cv2.rectangle(frame, (left, upper), (right, lower), (0,0,0), -1)
            
def start_moving():
    time.sleep(5)
    slave.send_command(f"DR{speed}")
 
if __name__ == "__main__":
    
    slave = Slave(reset_pin=23)
    slave.start()
    
    lane_detector = LaneDetector(n_windows=15, window_width=50)
    steering_controller = SteeringController()
    cam = Camera()
    cam.start()
    
    frames = 0
    start_fps = time.time()
    
    speed = 700
    thread = threading.Thread(target=start_moving, daemon=True)
    thread.start()
    
    try:
        while True:
            frame = cam.capture_array("main")
            frames += 1
            
            undistorted_frame = ImageProcessor.undistort_frame(frame)
            roi = ImageProcessor.extract_roi(undistorted_frame, 0.4)
            
            warped_roi = ImageProcessor.get_bird_eye_view(roi)
            warped_mask = ImageProcessor.preprocess_frame(roi)
            
            lane_detector.find_lanes(warped_mask, warped_roi)
            lane_detector.find_lanes_center(warped_roi)
            
            unwarped_roi = ImageProcessor.undo_bird_eye_view(warped_roi)
            undistorted_frame[undistorted_frame.shape[0]-unwarped_roi.shape[0]:, :, :] = unwarped_roi
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord("q") or key == 27:
                break
            
            cv2.imshow("frame", undistorted_frame)
            cv2.imshow("mask", warped_mask)
            cv2.imshow("warp", warped_roi)
            
            if frames >= 20:
                fps = (frames/(time.time() - start_fps))
                print(fps)
                
                frames = 0
                start_fps = time.time()
            
            lane_error_data = lane_detector.get_lane_data(warped_roi)
            if lane_error_data is None: continue
            
            position_error, angle_error, curvature_factor = lane_error_data
            
            speed_value = int(500 + (1000*(0.1-curvature_factor)/0.1))
            steer_value = steering_controller.get_steer_value(speed, position_error, angle_error)
            
            print("Action:", steer_value)
            #print(curvature_factor, speed_value)
            slave.send_command(f"SS{steer_value}")
            #slave.send_command(f"DR{speed_value}")
            
        cv2.destroyAllWindows()
        
    except KeyboardInterrupt:
        slave.send_command(f"DS")
        pass
