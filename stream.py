#!/usr/bin/env python3.8
import sys
import pyzed.sl as sl
from datetime import datetime

def main():

    init = sl.InitParameters()
    init.camera_resolution = sl.RESOLUTION.HD720
    init.depth_mode = sl.DEPTH_MODE.NONE
    #init.camera_fps = 30
    cam = sl.Camera()
    status = cam.open(init)
    if status != sl.ERROR_CODE.SUCCESS:
        print(repr(status))
        exit(1)

    runtime = sl.RuntimeParameters()

    stream = sl.StreamingParameters()
    stream.codec = sl.STREAMING_CODEC.H264
    stream.bitrate = 4000
    status = cam.enable_streaming(stream)
    if status != sl.ERROR_CODE.SUCCESS:
        print(repr(status))
        exit(1)

    print("  Quit : CTRL+C\n")
    timeName=""
    timeNum=0
    while True:
        err = cam.grab(runtime)
        tempTime = str(datetime.utcnow().strftime('%H:%M:%S.%f')[:-3])[0:8]
        if timeName != tempTime:
            print("FPS: {0}".format(str(timeNum)))
            timeNum = 0
            timeName = tempTime
        timeNum = timeNum + 1

    cam.disable_streaming()
    cam.close()

if __name__ == "__main__":
    main()
