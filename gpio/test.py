print("Welcome")
import Jetson.GPIO as GPIO
import time
GPIO.setmode(GPIO.BCM)
channel = 11
GPIO.cleanup(channel)
GPIO.setup(channel, GPIO.IN)

hit = False

last_sec = 0
count = 0
last_count = 0

def callback_one(channel):
    global n
    global count
    global last_sec
    global last_count
    n = (n + 1) % 2
    if n == 1:
        now = time.time()
        seconds = int(now % 60)
        if last_sec != seconds:
            last_sec = seconds
            last_count = count
            count = 0
        count = count+1
        current_speed_cms = count*35
        last_speed_cms = last_count*35
        last_speed_ms = last_speed_cms * 0.01
        last_speed_kmh = last_speed_ms * 3.6
        print("[{}] {}cm/s (last sec: {}cm/s | {}m/s | {}km/h)".format(seconds,current_speed_cms,last_speed_cms,last_speed_ms,last_speed_kmh))

print("Reading")
GPIO.add_event_detect(channel, GPIO.RISING)
GPIO.add_event_callback(channel, callback_one)

while not hit:
    time.sleep(1)

GPIO.cleanup(channel)
