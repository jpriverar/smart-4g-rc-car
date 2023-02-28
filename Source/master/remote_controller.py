from evdev import InputDevice, categorize, ecodes

#devices = [evdev.InputDevice(fn) for fn in evdev.list_devices()]
#for device in devices:
#    print(device.fn, device.name, device.phys)

class RemoteController(InputDevice):
    def __init__(self, dev_path):
        super().__init__(dev_path)
        
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
            print("You pressed down B")
        else:
            print("You lifted up B")

    def x_btn_handler(self, value):
        if value:
            print("You pressed down X")
        else:
            print("You lifted up X")

    def y_btn_handler(self, value):
        if value:
            print("You pressed down Y")
        else:
            print("You lifted up Y")

    def start_btn_handler(self, value):
        if value:
            print("You pressed down START")
        else:
            print("You lifted up START")

    def select_btn_handler(self, value):
        if value:
            print("You pressed down SELECT")
        else:
            print("You lifted up SELECT")

    def record_btn_handler(self, value):
        if value:
            print("You pressed down RECORD")
        else:
            print("You lifted up RECORD")

    def left_btn_handler(self, value):
        if value:
            print("You pressed down LB")
        else:
            print("You lifted up LB")
            
    def right_btn_handler(self, value):
        if value:
            print("You pressed down RB")
        else:
            print("You lifted up RB")

    def left_xjoy_handler(self, value):
        print(f"left xjoy: {value}")

    def left_yjoy_handler(self, value):
        print(f"left yjoy: {value}")

    def left_trig_handler(self, value):
        print(f"left trigger: {value}")

    def right_xjoy_handler(self, value):
        print(f"right xjoy: {value}")

    def right_yjoy_handler(self, value):
        print(f"right yjoy: {value}")

    def right_trig_handler(self, value):
        print(f"right trigger: {value}")

    def x_arrow_handler(self, value):
        print(f"x arrow: {value}")

    def y_arrow_handler(self, value):
        print(f"y arrow: {value}")



controller = RemoteController('/dev/input/event8')
controller.read_loop()