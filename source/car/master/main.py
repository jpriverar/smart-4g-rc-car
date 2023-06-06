import RPi.GPIO as GPIO
import time
import os
from rc_car import RC_Car
from slave import Slave

def is_connection_active(timeout=1):
    response = os.system("ping -c 1 " + REMOTE_HOST)
    return not response
    if response == 0:
        return True
    else:
      return False
    
def wait_for_network_connection():
    print("Waiting for internet connection...")
    honk_state = 0
    while True:
        if is_connection_active():
            car.slave.send_command("H0")
            honk_burst()
            print("Connection is active!")
            return
            
        else:
            honk_state ^= 1
            car.slave.send_command(f"H{honk_state}")
            time.sleep(2)
            
def honk_burst():
    for i in range(3):
        car.slave.send_command("H1")
        time.sleep(0.2)
        car.slave.send_command("H0")
        time.sleep(0.2)
    
if __name__ == "__main__":
    REMOTE_HOST = "192.168.1.4"
    #REMOTE_HOST = "3.134.62.14"
    REMOTE_CONTROL_PORT = 8485
    REMOTE_VIDEO_PORT = 8487
    
    car = RC_Car()
    #wait_for_network_connection() 
    
    car.attach_mqtt_client(REMOTE_HOST)
    car.attach_remote_control(REMOTE_HOST, REMOTE_CONTROL_PORT)
    car.attach_streamer(REMOTE_HOST, REMOTE_VIDEO_PORT)
    car.attach_gps()
    car.publish_current_configuration()
    
    car.start()
        
    try:
        while True:
            time.sleep(100)
    except KeyboardInterrupt:
        car.stop()
        GPIO.cleanup()