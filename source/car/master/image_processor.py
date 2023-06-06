import cv2
import numpy as np
import sys
import pickle
from camera import Camera

def load_mask_points(file_path):
    with open(file_path, "rb") as file:
        loaded_data = pickle.load(file)
    return loaded_data

def load_color_threshold(file_path):
    values = []
    file = open(file_path, 'r')
    for line in file.readlines():
        line_values = np.array([int(val.strip()) for val in line.split()])
        values.append(line_values)
    return values

def load_camera_params(file_path):
    with open(file_path, "rb") as file:
        loaded_data = pickle.load(file)
    return loaded_data


class ImageProcessor:
    K, D, rvecs, tvecs, = load_camera_params("/home/jp/Projects/smart-4g-rc-car/source/car/master/camera_calibration/camera_calibration_params.pckl")
    mask_points = np.array(load_mask_points("/home/jp/Projects/smart-4g-rc-car/source/car/master/mask_generation/mask_points.pckl"))
    thresholds = {"HSV": (load_color_threshold("/home/jp/Projects/smart-4g-rc-car/source/car/master/color_calibration/HSV_threshold_values"), cv2.COLOR_BGR2HSV),
                  "LAB": (load_color_threshold("/home/jp/Projects/smart-4g-rc-car/source/car/master/color_calibration/LAB_threshold_values"), cv2.COLOR_BGR2LAB)}
    
    @staticmethod
    def preprocess_frame(frame):        
        blur = cv2.GaussianBlur(frame, (5,5), 0)
        gray = cv2.cvtColor(blur, cv2.COLOR_RGB2GRAY)
        
        thresh, area_roi = cv2.threshold(gray,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (10, 3))
        area_roi = cv2.morphologyEx(area_roi, cv2.MORPH_CLOSE, kernel, iterations=5)
        area_roi = cv2.erode(area_roi, kernel, iterations=7)
        cv2.fillPoly(area_roi, pts=[ImageProcessor.mask_points], color=(0,0,0))
        #cv2.imshow("area otsu", area_roi)
        area_roi = ImageProcessor.get_bird_eye_view(area_roi)
        
        #thresh, lanes_roi = cv2.threshold(gray,0,255,cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
        #lanes_roi = cv2.morphologyEx(lanes_roi, cv2.MORPH_CLOSE, kernel)
        
        #dilated_otsu = cv2.dilate(otsu, (10,10), iterations=50)
        #eroded_otsu = cv2.erode(dilated_otsu, (5,5), iterations=10)
        
        #adaptive = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 21, 5)
        color = ImageProcessor.get_color_segmentation(ImageProcessor.get_bird_eye_view(blur))
        
        #cv2.imshow("lane otsu", lanes_roi)
        #cv2.imshow("adaptive", adaptive)
        #cv2.imshow("color", color)
        mask = ImageProcessor.bitwise_and_images([area_roi, color])
        return mask

    @staticmethod
    def get_color_segmentation(frame):
        color_thresholds = []
        for color_space, data in ImageProcessor.thresholds.items():
            color_frame = cv2.cvtColor(frame, data[1])
            color_thresh = cv2.inRange(color_frame, data[0][0], data[0][1])
            color_thresholds.append(color_thresh)
        return ImageProcessor.bitwise_and_images(color_thresholds)

    @staticmethod
    def bitwise_and_images(images):
        if len(images) == 0:
            return None

        result = images[0]
        for image in images[1:]:
            result = cv2.bitwise_and(result, image)
        return result
    
    @staticmethod
    def extract_roi(frame, roi_percentage):
        roi = frame[int(frame.shape[0]*(1-roi_percentage)):, :]
        return roi

    @staticmethod
    def get_bird_eye_view(frame):
        img_size = np.float32([(frame.shape[1], frame.shape[0])])

        src = np.float32([(0,0),(1,0),(0,1),(1,1)]) * img_size
        dst = np.float32([(0,0),(1,0),(0.425,1),(0.575,1)]) * img_size

        transformation_matrix = cv2.getPerspectiveTransform(src, dst)
        warped = cv2.warpPerspective(frame, transformation_matrix, (frame.shape[1], frame.shape[0]))
        return warped
    
    @staticmethod
    def undo_bird_eye_view(frame):
        img_size = np.float32([(frame.shape[1], frame.shape[0])])

        src = np.float32([(0,0),(1,0),(0,1),(1,1)]) * img_size
        dst = np.float32([(0,0),(1,0),(0.425,1),(0.575,1)]) * img_size

        transformation_matrix = cv2.getPerspectiveTransform(dst, src)
        warped = cv2.warpPerspective(frame, transformation_matrix, (frame.shape[1], frame.shape[0]))
        return warped
    
    @staticmethod
    def undistort_frame(frame):
        map1, map2 = cv2.fisheye.initUndistortRectifyMap(ImageProcessor.K, ImageProcessor.D, np.eye(3), ImageProcessor.K, frame.shape[:2][::-1], cv2.CV_16SC2)
        undistorted = cv2.remap(frame, map1, map2, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
        return undistorted
    
    @staticmethod
    def encode_frame(frame, compression_quality):
        result, encoded_frame = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), compression_quality])
        buffer = encoded_frame.tobytes()
        return buffer


if __name__ == "__main__":
    cam = Camera()
    cam.start()
    
    while True:
        frame = cam.capture_array("main")
        
        undistorted_frame = ImageProcessor.undistort_frame(frame)
        roi = ImageProcessor.extract_roi(undistorted_frame, 0.4)
        warped_roi = ImageProcessor.get_bird_eye_view(roi)
        color = ImageProcessor.get_color_segmentation(warped_roi)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q") or key == 27:
            break
        
        cv2.imshow("color", color)
        
    cv2.destroyAllWindows()
    
