import numpy as np
import cv2
from picamera2 import Picamera2
import pickle
import sys

sys.path.append("..")
from image_processor import ImageProcessor
from camera import Camera

def mouse_callback(event, x, y, flags, param):
    global mask_points
    if event == cv2.EVENT_LBUTTONDOWN:
        if y > 475: y = 480
        print(f"Clicked at ({x}, {y})")
        mask_points.append([x,y])
    
def save_mask_points(file_path, mask_points):
    with open(file_path, "wb") as file:
        pickle.dump(mask_points, file)
    print("Mask points data saved!")

def generate_mask():
    cam = Camera()
    
    # Defining initial values
    global mask_points
    mask_points = []

    # Creating named window
    window_name = 'Mask Generator'
    cv2.namedWindow(window_name)
    cv2.setMouseCallback(window_name, mouse_callback)

    try:
        cam.start()        
        while True:
            frame = cam.capture_array("main")
            undistorted_frame = ImageProcessor.undistort_frame(frame)
            roi = ImageProcessor.extract_roi(undistorted_frame, 0.4)
            
            if mask_points:
                cv2.fillPoly(roi, pts=[np.array(mask_points)], color=(0,255,0))
            
            # Checking if user wants to exit ('q' or esc)
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or key == 27: break

            cv2.imshow(window_name, roi)
        
        return mask_points
            
    except Exception as e: 
        print(e)

    finally:
        cv2.destroyAllWindows()
        
if __name__ == "__main__":
    mask_points = generate_mask()
    save_mask_points("mask_points.pckl", mask_points)