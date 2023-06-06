import pickle

class SteeringController:
    def __init__(self):
        self.speed_k_values = {700: (-0.035, -0.05),
                               800: (-0.05, -0.0333),
                               900: (-0.05, -0.0333),
                               1000: (-0.045, -0.027),
                               1100: (-0.05, -0.0333),
                               1200: (-0.05, -0.0333)}
    
    def get_steer_value(self, speed, pos_error, angle_error):
        k1, k2 = self.speed_k_values.get(speed, (-0.05, -0.0333))
        steer_input = k1*pos_error + k2*angle_error
        steer_value = int(steer_input*1024)
        steer_value = min(steer_value, 1024)
        steer_value = max(steer_value, -1023)
        return steer_value
        
