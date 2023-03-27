from picamera2 import Picamera2
import cv2
import socket

 # Creating the socket with the server
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('3.134.62.14', 8485))
connection = client_socket.makefile('wb')

# Creating and configuring the camera object
cam = Picamera2()
config = cam.create_preview_configuration(main={"size": (640, 480), "format":"RGB888"}, lores={"size": (320, 240), "format": "YUV420"})#, controls={"FrameDurationLimits": (16666, 16666)})
cam.configure(config)

img_counter = 0
encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]

# Start reading the video stream
cam.start()
while True:
    frame = cam.capture_array("main")
    
    # Encoding and serializing the frame
    result, encoded_frame = cv2.imencode('.jpg', frame, encode_param)
    data = encoded_frame.tobytes()
    size = len(data)

    # Sending the serialized frame through the socket
    print("{}: {}".format(img_counter, size))
    client_socket.sendall(size.to_bytes(4, byteorder="big"))
    client_socket.sendall(data)
  
    cv2.imshow('frame', frame)
  
    if cv2.waitKey(1) & 0xFF == ord('q'):
      break
    
    img_counter += 1
    
cam.stop()
cv2.destroyAllWindows()
      