#!/usr/bin/python3.9
from board import SCL_1, SDA_1
import busio
from adafruit_pca9685 import PCA9685
from adafruit_servokit import ServoKit

from adafruit_motor import servo
i2c = busio.I2C(SCL_1, SDA_1)
pca = PCA9685(i2c, address = 0x40)


#Kit = ServoKit(channels=16,address=0x57)

#Kit.servo[0].angle = 90
#Kit.servo[0].angle = 90
#Kit.servo[0].angle = 90

#Kit.continuous_servo[1].throttle = 0
#Kit.continuous_servo[1].throttle = 0.2

#Kit.continuous_servo[1].throttle = 0

#pca.frequency = 60
#led_channel = pca.channels[0]

#led_channel.duty_cycle = 0
#led_channel.duty_cycle = 0xffff
# Increase brightness:
#print("range startet")
#for i in range(0,0xffff,50):
#    led_channel.duty_cycle = i
#    print("i ",i)	
     
# Decrease brightness:
#for i in range(0xffff, 0, -50):
#    led_channel.duty_cycle = i

#from adafruit_servokit import ServoKit
#import board
#import busio
#import adafruit_pca9685

#print("i2c")
#i2c = busio.I2C(board.SCL, board.SDA)
#print("pca")
#pca = adafruit_pca9685.PCA9685(i2c)
#print("freuqency")

#pca.frequency = 60
#led_channel = pca.channels[0]

#led_channel.duty_cycle = 0
#led_channel.duty_cycle = 0xffff
# Increase brightness:
#print("range startet")
#for i in range(0,0xffff,50):
#    led_channel.duty_cycle = i
    #print("i ",i)	
     
# Decrease brightness:
#for i in range(0xffff, 0, -50):
#    led_channel.duty_cycle = i


#Kit = ServoKit(channels=16)

#Kit.servo[0].angle = 90
#Kit.servo[0].angle = 90
#Kit.servo[0].angle = 90

#Kit.continuous_servo[1].throttle = 0
#Kit.continuous_servo[1].throttle = 0.2

#Kit.continuous_servo[1].throttle = 0

