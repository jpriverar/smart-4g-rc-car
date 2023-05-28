import numpy as np
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

    cap = cv2.VideoCapture(cam_index)
    while cap.isOpened():
        ret, frame = cap.read()

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

def save_calibration_data(file_path, calibration_data):
    with open(file_path, "wb") as file:
        pickle.dump(calibration_data, file)
    print("Saved calibration data!")

def load_calibration_data(file_path):
    with open(file_path, "rb") as file:
        loaded_data = pickle.load(file)
    return loaded_data

def generate_object_points(pattern_size, square_size=1):
    m, n = pattern_size
    objp = np.zeros((n*m,3), np.float32)
    objp[:,:2] = np.mgrid[0:m,0:n].T.reshape(-1,2)
    return objp

def extract_image_points(img, pattern_size):
    improved_corners = None
    found, corners = cv2.findChessboardCorners(img, pattern_size, None)
    if found:
        termination_criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
        improved_corners = cv2.cornerSubPix(img, corners, (11,11), (-1,-1), termination_criteria)
    return found, improved_corners


if __name__ == "__main__":

    path = "/home/jprivera/Scripts/smart_4g_car/source/car/master/camera_calibration/pictures"
    PATTERN_SIZE = (9,6)

    #capture_images(cam_index=2, pattern_size=PATTERN_SIZE, image_directory=path)
    size, obj_points, img_points = get_calibration_points(path, PATTERN_SIZE)
    
    calibration_params = cv2.calibrateCamera(obj_points, img_points, size[::-1], None, None)
    if calibration_params[0]:
        save_calibration_data("camera_calibration_params.pckl", calibration_params[1:])


