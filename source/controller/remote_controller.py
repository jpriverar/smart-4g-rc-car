from evdev import InputDevice, categorize, ecodes
import subprocess
import os
import time
import sys
import threading

sys.path.append("../common")
from socket_relay_client import RelayClientUDP

class RemoteController(InputDevice):
    def __init__(self, host, port, dev_path, mqtt_publisher):
        # Creating the controller event reader
        if dev_path == "auto":
            event_dev = subprocess.run(["ls /dev/input/ | grep event | sort -V | tail -n1"], capture_output=True, text=True, shell=True)
            dev_path = os.path.join("/dev/input", event_dev.stdout.split("\n")[0])
            print(f"Using {dev_path} as controller")   
        super().__init__(dev_path)

        self.control_client = RelayClientUDP(host, port)
        self.publish_mqtt = mqtt_publisher

        # controller modes are: DRIVE, MENU, ...
        self.mode = "DRIVE"
        
        # camera movement modes are: ABS, INC, ...
        self.cam_move_mode = "ABS"
        self.long_press_thresh = 0.5
        self.event_start_time = 0 
        
        self.state_values = {"left_xjoy": 0,
                             "left_yjoy": 0,
                             "left_trig": 0,
                             "right_xjoy": 0,
                             "right_yjoy": 0,
                             "right_trig": 0,
                             "y_button": 0}
        
        # Handler functions for all buttons
        self.event_handlers = {(ecodes.EV_KEY, ecodes.BTN_A): self.a_btn_handler,
                               (ecodes.EV_KEY, ecodes.BTN_B): self.b_btn_handler,
                               (ecodes.EV_KEY, ecodes.BTN_X): self.x_btn_handler,
                               (ecodes.EV_KEY, ecodes.BTN_Y): self.y_btn_handler,
                               (ecodes.EV_KEY, ecodes.BTN_START): self.start_btn_handler,
                               (ecodes.EV_KEY, ecodes.BTN_SELECT): self.select_btn_handler,
                               (ecodes.EV_KEY, ecodes.KEY_RECORD): self.record_btn_handler,
                               (ecodes.EV_KEY, ecodes.BTN_TL): self.left_btn_handler,
                               (ecodes.EV_KEY, ecodes.BTN_TR): self.right_btn_handler,
                               (ecodes.EV_KEY, ecodes.BTN_THUMBR): self.right_joyBtn_handler,
                               (ecodes.EV_KEY, ecodes.BTN_THUMBL): self.left_joyBtn_handler,
                               (ecodes.EV_ABS, ecodes.ABS_X): self.left_xjoy_handler,
                               (ecodes.EV_ABS, ecodes.ABS_Y): self.left_yjoy_handler,
                               (ecodes.EV_ABS, ecodes.ABS_Z): self.left_trig_handler,
                               (ecodes.EV_ABS, ecodes.ABS_RX): self.right_xjoy_handler,
                               (ecodes.EV_ABS, ecodes.ABS_RY): self.right_yjoy_handler,
                               (ecodes.EV_ABS, ecodes.ABS_RZ): self.right_trig_handler,
                               (ecodes.EV_ABS, ecodes.ABS_RZ): self.right_trig_handler,
                               (ecodes.EV_ABS, ecodes.ABS_HAT0X): self.x_arrow_handler,
                               (ecodes.EV_ABS, ecodes.ABS_HAT0Y): self.y_arrow_handler,
                              }
        
    def start(self):
        self.control_client.heartbeat()
        controller_thread = threading.Thread(target=self.read_loop, daemon=True)
        controller_thread.start()

    def read_loop(self):
        for event in super().read_loop():
            self.handle_event(event)

    def handle_event(self, event):
        type, code, value = event.type, event.code, event.value
        if not type: return # Syncronisation event, does not need handler
        self.event_handlers.get((type, code), lambda _: print(f"Handler not defined for {categorize(event)}"))(value)

    def send_command(self, command):
        self.control_client.sendto(command)

    def a_btn_handler(self, value):
        if value: print("A button pressed")

    def b_btn_handler(self, value):
        if value:
            self.send_command("DS000\n".encode())

    def x_btn_handler(self, value):
        if value:
            self.send_command("H1000\n".encode())
        else:
            self.send_command("H0000\n".encode())

    def y_btn_handler(self, value):
        if value:
            if not self.state_values["y_button"]:
                self.send_command("L1000\n".encode())
            else: 
                self.send_command("L0000\n".encode())
            self.state_values["y_button"] ^= 1 

    def start_btn_handler(self, value):
        # Open the menu and change controller functions to MENU mode
        # Alternatively close the manu and switch back to DRIVE mode
        if value:
            if self.mode == "DRIVE":
                self.mode = "MENU"
            else:
                self.mode = "DRIVE"

    def select_btn_handler(self, value):
        if value:
            self.publish_mqtt(topic="RCCAR/CMD/SETUP", payload="1", qos=2) # 1 is just a dummy value, to send the signal

    def record_btn_handler(self, value):
        if value:
            self.publish_mqtt(topic="RCCAR/CMD/SAVE_CONFIG", payload="1", qos=2)

    def left_btn_handler(self, value):
        if value:
            self.send_command("VD000\n".encode())
            
    def right_btn_handler(self, value):
        if value:
            self.send_command("VU000\n".encode())
            
    def left_joyBtn_handler(self, value):
        if value:
            self.send_command("SC000\n".encode())
    
    def right_joyBtn_handler(self, value):
        if value:
            # Center camera
            self.send_command("PC000\n".encode())
            self.send_command("TC000\n".encode())
            
            # Start measuring for long press
            self.event_start_time = time.time()
        else:
            # Check how long the button was pressed before released
            if time.time() - self.event_start_time >= self.long_press_thresh:
                self.cam_move_mode = "INC" if self.cam_move_mode == "ABS" else "ABS"

    def left_xjoy_handler(self, value):
        if abs(value - self.state_values["left_xjoy"]) >= 100:
            value /= 32768
            input_val = int(-value*1024)
            self.send_command(f"SS{input_val}\n".encode())
            self.state_values["left_xjoy"] = value

    def left_yjoy_handler(self, value):
        pass

    def left_trig_handler(self, value):
        self.send_command(f"VB{value}\n".encode())
        
        self.state_values["left_trig"] = value

    def right_xjoy_handler(self, value):
        if abs(value - self.state_values["right_xjoy"]) >= 200:
            value /= 32768
            input_val = int(-value*1024)
            
            if self.cam_move_mode == "ABS":
                self.send_command(f"PS{input_val}\n".encode())
    
            elif self.cam_move_mode == "INC":
                if abs(input_val) < 250: input_val = 0
                self.send_command(f"PV{input_val}\n".encode())
                
            self.state_values["right_xjoy"] = value
        
    def right_yjoy_handler(self, value):
        if abs(value - self.state_values["right_yjoy"]) >= 200:
            value /= 32768
            input_val = int(-value*1024)
            
            if self.cam_move_mode == "ABS":
                self.send_command(f"TS{input_val}\n".encode())
    
            elif self.cam_move_mode == "INC":
                if abs(input_val) < 250: input_val = 0
                self.send_command(f"TV{input_val}\n".encode())
                
            self.state_values["right_yjoy"] = value

    def right_trig_handler(self, value):
        value = int((value/1023)*100)
        self.send_command(f"DP{value}\n".encode())

        self.state_values["right_trig"] = value

    def x_arrow_handler(self, value):
        if value == 1:
            self.send_command("PD1024\n".encode())
        elif value == -1:
            self.send_command("PI1024\n".encode())
        
    def y_arrow_handler(self, value):
        if value == 1:
            self.send_command("TI1024\n".encode())
        elif value == -1:
            self.send_command("TD1024\n".encode())