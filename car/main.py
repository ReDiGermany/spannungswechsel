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

has_car = False
Kit = None
pca = None



def on_button_pressed(button):
    print('Button {0} was pressed'.format(button.name))
    if(has_car):
        Kit.servo[1].angle = 90
        Kit.continuous_servo[0].throttle = 0


def on_button_released(button):
    print('Button {0} was released'.format(button.name))


def on_axis_moved(axis):
    if axis.name == "axis_l":
        val = (90 - ((axis.x)*10))
        if(val > 80 and val < 100):
            val = 90
        # print(val)
        if(has_car):
            print("angle = "+str(val))
            Kit.servo[1].angle = val

    if axis.name == "axis_r":
        val = (axis.x * -1)/4
        if(val < 0.1 and val > -0.1):
            val = 0
        # print(val)
        if(has_car):
            print("speed = "+str(val))
            Kit.continuous_servo[0].throttle = val

def thread_function():
    was_running = False
    while True:
        try:
            stdoutdata = sp.getoutput("hcitool con")
            if "EC:83:50:95:D3:A7" in stdoutdata.split():
                if was_running == False:
                    was_running=True
                    print("Controller is connected")
            else:
                print("Controller is not connected")
                if was_running:
                    print("Controller was connected - shutting down!")
                    if(has_car):
                        Kit.servo[1].angle = 90
                        Kit.continuous_servo[0].throttle = 0
                    os.system("shutdown now -h")

        except:
            print("no")

@click.command()
@click.option('--car', default=False, help='number of greetings',is_flag=True)
def hello(car):

    whoami = sp.getoutput("whoami")
    if whoami!="root":
        print("Need to run as root!")
        quit()


    if(car):
        global has_car
        global Kit
        global pca
        has_car = True
        i2c = busio.I2C(SCL_1, SDA_1)
        pca = PCA9685(i2c, address = 0x40)

        Kit = ServoKit(channels=16,i2c=i2c)
        print("Servo initiated!")
    # x = threading.Thread(target=thread_function)
    # x.start()

    try:
        with Xbox360Controller(0, axis_threshold=0.2) as controller:
            # Button A events
            controller.button_a.when_pressed = on_button_pressed
            controller.button_a.when_released = on_button_released

            # Left and right axis move event
            controller.axis_l.when_moved = on_axis_moved
            controller.axis_r.when_moved = on_axis_moved

            # controller.axis_threshold = 0.05

            signal.pause()
    except KeyboardInterrupt:
        pass
    x.join()

if __name__ == '__main__':
    hello()
