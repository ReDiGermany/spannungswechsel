"""
    Read a stream and display the left images using OpenCV
"""
import sys
import pyzed.sl as sl
import cv2
from datetime import datetime
import time

def current_milli_time():
    return time.time_ns()
    # return round(time.time() * 1000)

def main():
    init = sl.InitParameters()
    init.camera_resolution = sl.RESOLUTION.HD720
    init.depth_mode = sl.DEPTH_MODE.PERFORMANCE
    init.camera_fps = 50

    if (len(sys.argv) > 1) :
        ip = sys.argv[1]
        init.set_from_stream(ip)
    else :
        print('Usage: python receiver.py {ip}')
        exit(1)

    cam = sl.Camera()
    status = cam.open(init)
    if status != sl.ERROR_CODE.SUCCESS:
        print(repr(status))
        exit(1)

    runtime = sl.RuntimeParameters()
    mat = sl.Mat()

    print("  Quit : CTRL+C\n")
    timeName=""
    timeNum=0
    while True:
        err = cam.grab(runtime)
        if (err == sl.ERROR_CODE.SUCCESS) :
            cam.retrieve_image(mat, sl.VIEW.LEFT)
            # print("time: {}".format((time.time_ns()-mat.timestamp.data_ns) / 1e9))
            tm = str(datetime.utcnow().strftime('%H:%M:%S.%f')[:-3])
            # print("image-{}.jpg".format(tm))
            # cv2.imwrite("images/image-{}.jpg".format(datetime.utcnow().strftime('%H%M%S.%f')), mat.get_data())

            tempTime = tm[0:8]
            if timeName != tempTime:
                print("FPS: {0}".format(str(timeNum)))
                timeNum = 0
                timeName = tempTime
            timeNum = timeNum + 1

            # cv2.imshow("ZED", mat.get_data())
            # key = cv2.waitKey(1)
        else:
            print("error")

    cam.close()

if __name__ == "__main__":
    main()