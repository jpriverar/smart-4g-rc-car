import numpy as np
from picamera2 import Picamera2
import cv2
import shutil
import os
import glob
import pickle

def capture_images(cam_index, pattern_size, image_directory):
    shutil.rmtree(image_directory, ignore_errors=True)
    os.mkdir(image_directory)

    calibration_images_saved = 0

    def get_color():
        color = (255,255,255)
        if calibration_images_saved >= 15:
            color = (0,255,0)
        return color

    cam = Picamera2()
    config = cam.create_preview_configuration(main={"size": (640, 480), "format":"RGB888"})
    cam.configure(config)
    cam.start()
    
    while True:
        frame = cam.capture_array("main")

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q') or key == 27:
            break

        found, corners = extract_image_points(gray, pattern_size)
        
        if found:
            if key == 32: # Pressed space bar
                calibration_images_saved += 1
                print("Calibration image saved")

                if image_directory:
                    cv2.imwrite(f"{image_directory}/img{calibration_images_saved}.jpg", gray)
                    print("Frame saved")

            cv2.drawChessboardCorners(frame, pattern_size, corners, found)

        cv2.putText(frame, text=f"{calibration_images_saved}", org=(10,50), fontFace=cv2.FONT_HERSHEY_DUPLEX, fontScale=1, color=get_color())
        cv2.imshow('frame', frame)

    cv2.destroyAllWindows()

def get_calibration_points(path, pattern_size):
    images = glob.glob(f"{path}/*.jpg")
    if not images: return

    size = cv2.imread(images[0], cv2.IMREAD_GRAYSCALE).shape

    img_points = []
    obj_points = []

    for image in images:
        gray = cv2.imread(image, cv2.IMREAD_GRAYSCALE)
        found, corners = extract_image_points(gray, pattern_size)

        if found:
            img_points.append(corners)
            obj_points.append(generate_object_points(pattern_size))
    
    print(f"Extracted {len(obj_points)}/{len(images)} sets of calibration points")
    return size, obj_points, img_points

def save_camera_params(file_path, calibration_data):
    with open(file_path, "wb") as file:
        pickle.dump(calibration_data, file)
    print("Saved calibration data!")

def generate_object_points(pattern_size, square_size=1):
    m, n = pattern_size
    objp = np.zeros((n*m,3), np.float32)
    objp[:,:2] = np.mgrid[0:m,0:n].T.reshape(-1,2)
    return objp

def extract_image_points(img, pattern_size):
    subpix_criteria = (cv2.TERM_CRITERIA_EPS+cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
    
    found, corners = cv2.findChessboardCorners(img, pattern_size, cv2.CALIB_CB_ADAPTIVE_THRESH+cv2.CALIB_CB_FAST_CHECK+cv2.CALIB_CB_NORMALIZE_IMAGE)
    if found:
        cv2.cornerSubPix(img, corners, (11,11), (-1,-1), subpix_criteria)
    return found, corners


if __name__ == "__main__":

    path = "/home/jp/Projects/smart-4g-rc-car/source/car/master/camera_calibration/pictures"
    PATTERN_SIZE = (9,6)

    #capture_images(cam_index=2, pattern_size=PATTERN_SIZE, image_directory=path)
    size, obj_points, img_points = get_calibration_points(path, PATTERN_SIZE)
    obj_points = np.expand_dims(np.asarray(obj_points), -2)
    
    K = np.zeros((3, 3), dtype=np.float64)
    D = np.zeros((4, 1), dtype=np.float64)
    rvecs = [np.zeros((1, 1, 3), dtype=np.float64) for i in range(len(obj_points))]
    tvecs = [np.zeros((1, 1, 3), dtype=np.float64) for i in range(len(obj_points))]
    calibration_flags = cv2.fisheye.CALIB_RECOMPUTE_EXTRINSIC + cv2.fisheye.CALIB_CHECK_COND + cv2.fisheye.CALIB_FIX_SKEW
    
    ret,_,_,_,_ = cv2.fisheye.calibrate(obj_points, img_points, size[::-1], K, D, rvecs, tvecs, calibration_flags, (cv2.TERM_CRITERIA_EPS+cv2.TERM_CRITERIA_MAX_ITER, 30, 1e-6))
    
    if ret:
        save_camera_params("camera_calibration_params.pckl", (K, D, rvecs, tvecs))



