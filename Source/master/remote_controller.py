from evdev import InputDevice, categorize, ecodes
import subprocess
import os

#devices = [evdev.InputDevice(fn) for fn in evdev.list_devices()]
#for device in devices:
#    print(device.fn, device.name, device.phys)

class RemoteController(InputDevice):
    def __init__(self, dev_path="auto", uart_messenger=None):
        if dev_path == "auto":
            event_dev = subprocess.run(["ls /dev/input/ | grep event | sort -V | tail -n1"], capture_output=True, text=True, shell=True)
            dev_path = os.path.join("/dev/input", event_dev.stdout.split("\n")[0])
            print(dev_path)
            
        super().__init__(dev_path)
        
        self.messenger = uart_messenger
        self.mode = "drive"
        
        self.state_values = {"left_xjoy": 0,
                             "left_yjoy": 0,
                             "left_trig": 0,
                             "right_xjoy": 0,
                             "right_yjoy": 0,
                             "right_trig": 0}
        
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

    def read_loop(self):
        for event in super().read_loop():
            self.handle_event(event)

    def handle_event(self, event):
        type, code, value = event.type, event.code, event.value
        if not type: return # Syncronisation event, does not need handler
        self.event_handlers.get((type, code), lambda _: print(f"Handler not defined for {categorize(event)}"))(value)

    def a_btn_handler(self, value):
        if value:
            print("You pressed down A")
        else:
            print("You lifted up A")

    def b_btn_handler(self, value):
        if value:
            self.messenger.send_msg("IO")
        else:
            print("You lifted up B")

    def x_btn_handler(self, value):
        if value:
            self.messenger.send_msg("FO")
        else:
            print("You lifted up X")

    def y_btn_handler(self, value):
        pass

    def start_btn_handler(self, value):
        pass

    def select_btn_handler(self, value):
        pass

    def record_btn_handler(self, value):
        pass

    def left_btn_handler(self, value):
        pass
            
    def right_btn_handler(self, value):
        pass
            
    def left_joyBtn_handler(self, value):
        pass
    
    def right_joyBtn_handler(self, value):
        pass

    def left_xjoy_handler(self, value):
        if abs(value - self.state_values["left_xjoy"]) >= 100:
            value /= 32768
            input_val = int(-value*1024)
            self.messenger.send_msg(f"SS{input_val}")
            self.state_values["left_xjoy"] = value # Updating value

    def left_yjoy_handler(self, value):
        pass

    def left_trig_handler(self, value):
        pass

    def right_xjoy_handler(self, value):
        if abs(value - self.state_values["right_xjoy"]) >= 100:
            value /= 32768
            input_val = int(-value*1024)
            self.messenger.send_msg(f"PS{input_val}")
            self.state_values["right_xjoy"] = value # Updating value
        
        
    def right_yjoy_handler(self, value):
        if abs(value - self.state_values["right_xjoy"]) >= 100:
            value /= 32768
            input_val = int(-value*1024)
            self.messenger.send_msg(f"TS{input_val}")
            self.state_values["right_yjoy"] = value # Updating value

    def right_trig_handler(self, value):
        value /= 1024
        power_val = int(value*50)
        #self.messenger.send_msg(f"DP{power_val}")

    def x_arrow_handler(self, value):
        if value == 1:
            self.messenger.send_msg("PD1024")
        elif value == -1:
            self.messenger.send_msg("PI1024")
        
    def y_arrow_handler(self, value):
        if value == 1:
            self.messenger.send_msg("TI1024")
        elif value == -1:
            self.messenger.send_msg("TD1024")


if __name__ == "__main__":
    controller = RemoteController('auto')
    controller.read_loop()
