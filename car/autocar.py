import sys
import torch
import torchvision
import numpy as np
from board import SCL, SDA
from pyPS4Controller.controller import Controller
import camera
import cv2
import csv
from uuid import uuid1
import neural_network
from adafruit_servokit import ServoKit
import time

class Autocar():
    #calibrated on my tt-02 (0.2;0.13)
    steering_offset = 0.2
    throttle_offset = 0.13
    #first set to 1.0 and then check with calibrate functions to find max of each side, then use this values
    throttle_gain = 0.1
    steering_gain = 0.5
    
    
    def __init__(self):
        
        
        self.kit = ServoKit(channels=16, address=0x40)
        self.steering_motor = self.kit.continuous_servo[0]
        self.throttle_motor = self.kit.continuous_servo[1]
        self.steering_motor.throttle = self.steering_offset
        self.throttle_motor.throttle = self.throttle_offset

        # init model
        
        model = neural_network.Net()
        self.model = model.eval()
        self.model.load_state_dict(torch.load('model/autopilot.pt'))
        self.device = torch.device('cuda')
        self.model.to(self.device)
        
        # init vars
        self.temp = 0
        mean = 255.0 * np.array([0.485, 0.456, 0.406])
        stdev = 255.0 * np.array([0.229, 0.224, 0.225])
        self.normalize = torchvision.transforms.Normalize(mean, stdev)
        self.angle_out = 0

        # init Camera
        self.cam = camera.Camera()        

        # initial content
        with open('control_data.csv','w') as f:
            f.write('date,steering,speed\n')
        
    def calibrate_steering(self):
        #checks from -0.4 to 0.4 to find center of steering
        for x in range(-4,4,1):
            current_value = (x/10)+self.steering_offset
            self.steering_motor.throttle=self.scale_values(current_value)
            print(x/10)
            time.sleep(1)
     
    def calibrate_throttle(self):
        #checks from -0.25 to 0.25 to find values where motor do not run
        for x in range(-25,25,1):
            current_value = (x/100)+self.throttle_offset
            self.throttle_motor.throttle=self.scale_values(current_value)
            print(x/100)
            time.sleep(0.5)
    
    def reset(self):
        #set steering to center and motor to stop
        self.steering_motor.throttle = self.steering_offset
        self.throttle_motor.throttle = self.throttle_offset
        
    def drive(self, axis_data):
        # scaled values should be between -1 and 1. Values are multiplied with max (gain)
        x = axis_data[0]
        steering = self.scale_values(x) * self.steering_gain
        print(steering)
        self.steering_motor.throttle = steering
        y = axis_data[1]
        throttle = self.scale_values(y) * self.throttle_gain
        print(throttle)
        self.throttle_motor.throttle = throttle
  
    def scale_values(self, x):
        if x < -1:
            return -1
        elif x > 1:
            return 1
        else:
            return x
        
    def save_data(self, axis_data):
    
        count = self.cam.count
        img = self.cam.value

        if count!= self.temp:
        
            num = uuid1()
            cv2.imwrite('images/'+str(num)+".jpg", img)
            
            # append inputs to csv
            with open('control_data.csv','a',newline='') as f:
                writer=csv.writer(f)
                writer.writerow([num,axis_data[0],axis_data[1]])
                
            self.temp = count
            
            print('Save data!')
            
        else:
            pass
        
            
    def preprocess(self, camera_value):
    
        x = camera_value
        x = cv2.resize(x, (224, 224))
        x = cv2.cvtColor(x, cv2.COLOR_BGR2RGB)
        x = x.transpose((2, 0, 1))
        x = torch.from_numpy(x).float()
        x = self.normalize(x)
        x = x.to(self.device)
        x = x[None, ...]
        
        return x        
    
    def autopilot(self):
        
        img = self.preprocess(self.cam.value)
        count = self.cam.count
        
        if count!= self.temp:
            print('RUN!')
            self.model.eval()
            with torch.no_grad():
                output = self.model(img)
            outnump = output.cpu().data.numpy()
            
            if outnump >= 1:
                self.angle_out = [[1]]
                
            elif outnump <= -1:
                self.angle_out = [[-1]]
            else:
                self.angle_out = outnump
                
            print(self.angle_out[0][0])
            
            self.temp = count
            
            
        else:
            pass
        
        self.drive({0:self.angle_out[0][0],1:0.0,2:0.0,3:-1.0,4:1,5:0.0})
        
    
        

        
