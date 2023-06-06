from picamera2 import Picamera2

class Camera(Picamera2):
    def __init__(self):
        super().__init__()
        config = self.create_preview_configuration(main={"size": (640, 480), "format":"RGB888"}, controls={"FrameRate":30})
        self.configure(config)
        self.resolution = "640x480"
                           