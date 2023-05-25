from picamera2 import Picamera2
import cv2
import socket

 # Creating the socket with the server
#client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#client_socket.connect(('3.134.62.14', 8485))
#connection = client_socket.makefile('wb')

# Creating and configuring the camera object
cam = Picamera2()
print(cam.camera_controls)
config = cam.create_preview_configuration(main={"size": (640, 480), "format":"RGB888"}, lores={"size": (320, 240), "format": "YUV420"}, controls={"FrameRate":25, "Sharpness":5.0, "AwbEnable":True})
cam.align_configuration(config)
cam.configure(config)

cam.controls.ExposureTime = 50000

img_counter = 0
encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]

# Start reading the video stream
cam.start()
while True:
    frame = cam.capture_array("lores")
    print(frame.shape)
    
    # Encoding and serializing the frame
    #result, encoded_frame = cv2.imencode('.jpg', frame, encode_param)
    #data = encoded_frame.tobytes()
    #size = len(data)

    # Sending the serialized frame through the socket
    #print("{}: {}".format(img_counter, size))
    #client_socket.sendall(size.to_bytes(4, byteorder="big"))
    #client_socket.sendall(data)
  
    cv2.imshow('frame', frame)
  
    if cv2.waitKey(1) & 0xFF == ord('q'):
      break
    
    img_counter += 1
    
cam.stop()
cv2.destroyAllWindows()