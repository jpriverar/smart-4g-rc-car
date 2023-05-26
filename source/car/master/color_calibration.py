import cv2
import numpy as np

def on_low_0_thresh_trackbar(val):
    global low_vals
    low_vals[0] = val
    #print('LOW', low_vals)

def on_high_0_thresh_trackbar(val):
    global high_vals
    high_vals[0] = val
    #print('HIGH', high_vals)
    
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

def save_calibration_values(file_path, low_vals, high_vals):
    file = open(file_path, 'w')
    for val in low_vals: file.write(f'{val} ')
    file.write('\n')
    for val in high_vals: file.write(f'{val} ')
    file.close()

def get_calibration_values(file_path):
    values = []
    file = open(file_path, 'r')
    for line in file.readlines():
        line_values = np.array([int(val) for val in line.split()])
        values.append(line_values)
    return values

def calibrate():
    cap = cv2.VideoCapture(2)
    
    # Defining initial values
    global low_vals, high_vals, max_vals
    low_vals = np.array([0, 0, 0])
    high_vals = np.array([180, 255, 255])

    # Defining maximum values
    max_vals = [180,255,255]

    # Creating named window
    window_name = 'Color Calibrator'
    cv2.namedWindow(window_name)

    # Creating trackbars
    for i, channel in enumerate("HSV"):
        cv2.createTrackbar(f'Low {channel}', window_name, low_vals[i], max_vals[i], globals()[f'on_low_{i}_thresh_trackbar'])
        cv2.createTrackbar(f'High {channel}', window_name, high_vals[i], max_vals[i], globals()[f'on_high_{i}_thresh_trackbar'])

    if not cap.isOpened():
        raise  RuntimeError("Unable to read camera feed")
        
    try:
        while cap.isOpened():
            ret, frame =  cap.read()
            if frame is None:
                print('No frame')
                break

            # Color space mapping
            hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

            # Masking based of user values
            mask = cv2.inRange(hsv_frame, low_vals, high_vals)
            masked = cv2.bitwise_and(frame, frame, mask=mask)
            
            # Checking if user wants to exit ('q' or esc)
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or key == 27: break

            cv2.imshow(window_name, masked)
        
        return low_vals, high_vals
            
    except Exception as e: 
        print(e)

    finally:
        cap.release()
        cv2.destroyAllWindows()

    
if __name__ == '__main__':
    low_vals, high_vals = calibrate()
    save_calibration_values("./threshold_values", low_vals, high_vals)