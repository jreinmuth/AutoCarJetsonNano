import sys
from autocar import Autocar
from pyPS4Controller.controller import Controller


class PS4CarController(Controller):

    max_value_stick = 30000
    
    def __init__(self, **kwargs):
        Controller.__init__(self, **kwargs)
        self.car = Autocar()
        self.axis_data = {0:0.0,1:0.0} #default
        self.train = True
    
    def on_circle_release(self):
        self.train = False
        print("Terminate training")
    
    def on_circle_press(self):
        self.train = True
        print("Start training")
        
    def on_square_press(self):
        self.train = False
        print("Start autopilot")
        #self.car.autopilot
        
    def on_square_release(self):
        self.train = False
        print("Stop autopilot")
        #self.car.autopilot
    
    def on_triangle_press(self):
        self.train = True
        print("Reset car")
        self.car.reset
        
    def on_triangle_release(self):
        self.train = True
        print("Reset car")
        self.car.reset
        self.axis_data = {0:0.0,1:0.0}
        
    def on_L2_press(self,value_from_stick):
        print("Left/Right movement")
        self.axis_data[0]=value_from_stick / self.max_value_stick
        if self.train:
            self.car.drive(self.axis_data)
            self.car.save_data(self.axis_data)
            
    def on_R2_press(self,value_from_stick):
        print("Up/Down movement")
        #forward -> negative numbers
        self.axis_data[1]=value_from_stick / self.max_value_stick
        if self.train:
            self.car.drive(self.axis_data)
            self.car.save_data(self.axis_data)
            
    def on_L2_release(self):
        print("Joystick centered)
        self.axis_data[0]=0.0
        if self.train:
            self.car.drive(self.axis_data)
            self.car.save_data(self.axis_data)
        
    def on_R2_release(self):    
        print("Joystick centered")
        self.axis_data[1]=0.0
        if self.train:
            self.car.drive(self.axis_data)
            self.car.save_data(self.axis_data)
            
    def on_options_release(self):
        self.car.calibrate_steering()
        self.car.reset()
        self.car.calibrate_throttle()
        self.car.reset()
        
            
if __name__ == "__main__":
    
    
    # init gamepad controller
    ps4 = PS4CarController(interface="/dev/input/js0", connecting_using_ds4drv=False)
    
        
    try:
        ps4.listen(timeout=60)

            
    except KeyboardInterrupt:
            car.pca.deinit()
            sys.exit(0)
        
