import cv2
import time

cap = cv2.VideoCapture(0)
print('Waiting for the camera module to initialize...')
time.sleep(5)

while cap.isOpened():

    ret, frame = cap.read()
    
    if not ret:
        print('No frame...')
        break

    key = cv2.waitKey(1)
    if key == ord('q') or key == 27: break

    cv2.imshow('frame', frame)

cap.release()
cv2.destroyAllWindows()
