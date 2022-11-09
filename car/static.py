#!/usr/bin/python3.9
import signal
import click

from xbox360controller import Xbox360Controller

from board import SCL_1, SDA_1
import busio
import time
from adafruit_pca9685 import PCA9685
from adafruit_servokit import ServoKit

from adafruit_motor import servo
import subprocess as sp
import threading
import os

print("imports done")

has_car = False
Kit = None
pca = None

has_car = True
i2c = busio.I2C(SCL_1, SDA_1)
print("i2c done")
pca = PCA9685(i2c, address = 0x40)
print("pca done")

Kit = ServoKit(channels=16,i2c=i2c)
print("Servo initiated!")
Kit.continuous_servo[0].throttle = 0.2
print("0.2")
time.sleep(1)
Kit.continuous_servo[0].throttle = 0.0
print("0")
