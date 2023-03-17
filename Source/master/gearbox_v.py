
class Gearbox:
    def __init__(self):
        
        self.curr_gear = 1
        
        # Min and max rpm per gear
        self.gear_speed_ranges = {0:(-10, 0),
                                  1:(0, 50),
                                  2:(51, 100),
                                  3:(101, 150),
                                  3:(151, 200),
                                  4:(201, 250),
                                  5:(251, 300),
                                  6:(301, 350)}
    
    def shift_gear_up(self, value):
        pass
    
    def shift_gear_down(self, value):
        pass