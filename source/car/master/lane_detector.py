from color_calibration import get_calibration_values
from picamera2 import Picamera2
import numpy as np
import cv2

class LaneDetector:
    def __init__(self):
        self.low_threshold = np.array([0,0,0])
        self.high_threshold = np.array([180,255,255])

    def load_threshold_values(self, file_path):
        low_thresh, high_thresh = get_calibration_values(file_path)
        self.low_threshold = low_thresh
        self.high_threshold = high_thresh

    def preprocess_frame(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        
        # Otsu's thresholding after Gaussian filtering
        blur = cv2.GaussianBlur(gray, (5,5), 0)
        thresh, mask = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        #hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        #mask = cv2.inRange(hsv_frame, self.low_threshold, self.high_threshold)
        return mask

    def perspective_warp(self, frame):
        dst_size = (1280, 720)
        img_size = np.float32([(frame.shape[1], frame.shape[0])])

        src = np.float32([(0,0.6),(1,0.6),(0,1),(1,1)])
        dst = np.float32([(0,0),(1,0),(0,1),(1,1)])

        src = src* img_size
        dst = dst * img_size#np.float32(dst_size)

        transformation_matrix = cv2.getPerspectiveTransform(src, dst)
        warped = cv2.warpPerspective(frame, transformation_matrix, (frame.shape[1], frame.shape[0]))
        return warped


if __name__ == "__main__":

    lane_detector = LaneDetector()
    lane_detector.load_threshold_values('./threshold_values')
    
    cam = Picamera2()
    config = cam.create_preview_configuration(main={"size": (640, 480), "format":"RGB888"})
    cam.configure(config)
    cam.start()

    #cap = cv2.VideoCapture(2)
    #while cap.isOpened():
    #    ret, frame = cap.read()
    #
    #    if not ret:
    #        print("No frame")
    #        continue
    
    while True:
        frame = cam.capture_array("main")
        preprocessed = lane_detector.preprocess_frame(frame)
        warped = lane_detector.perspective_warp(frame)

        cv2.imshow("frame", frame)
        cv2.imshow("preprocessed", preprocessed)
        cv2.imshow("warped", warped)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q') or key == 27:
            break

    #cap.release()
    cv2.destroyAllWindows()



