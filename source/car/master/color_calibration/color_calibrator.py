import cv2
import numpy as np
from picamera2 import Picamera2
import sys

sys.path.append("..")
from image_processor import ImageProcessor
from camera import Camera

def on_low_0_thresh_trackbar(val):
    global low_vals
    low_vals[0] = val

def on_high_0_thresh_trackbar(val):
    global high_vals
    high_vals[0] = val
    
def on_low_1_thresh_trackbar(val):
    global low_vals
    low_vals[1] = val

def on_high_1_thresh_trackbar(val):
    global high_vals
    high_vals[1] = val
    
def on_low_2_thresh_trackbar(val):
    global low_vals
    low_vals[2] = val
    
def on_high_2_thresh_trackbar(val):
    global high_vals
    high_vals[2] = val

def save_color_threshold(file_path, low_vals, high_vals):
    file = open(file_path, 'w')
    for val in low_vals: file.write(f'{val} ')
    file.write('\n')
    for val in high_vals: file.write(f'{val} ')
    file.close()
    print(f"Saved thresholds in {file_path}")

def calibrate(color_space):
    cam = Camera()
    
    color_transformations = {"HSV": cv2.COLOR_BGR2HSV,
                             "LAB": cv2.COLOR_BGR2LAB,
                             "RGB": cv2.COLOR_BGR2RGB}
    
    # Defining initial values
    global low_vals, high_vals, max_vals
    low_vals = np.array([0, 0, 0])
    high_vals = np.array([255, 255, 255])

    # Defining maximum values
    max_vals = [255,255,255]

    # Creating named window
    window_name = 'Color Calibrator'
    cv2.namedWindow(window_name)

    # Creating trackbars
    for i, channel in enumerate(color_space):
        cv2.createTrackbar(f'Low {channel}', window_name, low_vals[i], max_vals[i], globals()[f'on_low_{i}_thresh_trackbar'])
        cv2.createTrackbar(f'High {channel}', window_name, high_vals[i], max_vals[i], globals()[f'on_high_{i}_thresh_trackbar'])
        
    cam.start()        
    while True:
        frame = cam.capture_array("main")
        undistorted_frame = ImageProcessor.undistort_frame(frame)
        roi = ImageProcessor.extract_roi(undistorted_frame, 0.4)
        warped_roi = ImageProcessor.get_bird_eye_view(roi)

        # Color space mapping
        new_color_frame = cv2.cvtColor(warped_roi, color_transformations[color_space])

        # Masking based of user values
        mask = cv2.inRange(new_color_frame, low_vals, high_vals)
        masked = cv2.bitwise_and(warped_roi, warped_roi, mask=mask)
        
        # Checking if user wants to exit ('q' or esc)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q') or key == 27: break

        cv2.imshow(window_name, masked)
    
    cv2.destroyAllWindows()
    return low_vals, high_vals

    
if __name__ == '__main__':
    color_space = "LAB"
    
    low_vals, high_vals = calibrate(color_space)
    save_color_threshold(f"./{color_space}_threshold_values", low_vals, high_vals)