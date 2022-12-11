#!/usr/bin/env python3.8

from __future__ import division
import matplotlib.pyplot as plt

from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import math
import numpy as np
import json 

from data import DataStore
import external_functions
import server

import argparse
import torch
import cv2
import pyzed.sl as sl

from threading import Lock, Thread
import time
from datetime import datetime

import sys
sys.path.insert(0, './yolov5')
from models.experimental import attempt_load
from utils.general import check_img_size, non_max_suppression
from utils.torch_utils import select_device

lock = Lock()
run_signal = False
exit_signal = False

pylons = ["blue","green","orange","pink","yellow"]

bizzi = True
def plt_thread(weights, img_size, conf_thres=0.2, iou_thres=0.45):
    global image_net, exit_signal, run_signal, detections
    print("Initializing Camera...")


    zed = sl.Camera()
    input_type = sl.InputType()
    if opt.svo is not None:
        input_type.set_from_svo_file(opt.svo)

    # Create a InitParameters object and set configuration parameters
    init_params = sl.InitParameters(input_t=input_type, svo_real_time_mode=True)
    init_params.camera_resolution = sl.RESOLUTION.HD1080
    init_params.coordinate_units = sl.UNIT.CENTIMETER
    init_params.coordinate_system = sl.COORDINATE_SYSTEM.LEFT_HANDED_Y_UP
    init_params.depth_mode = sl.DEPTH_MODE.ULTRA  # QUALITY
    # init_params.depth_maximum_distance = 20

    runtime_params = sl.RuntimeParameters()
    status = zed.open(init_params)
    # zed.set_camera_settings(sl.VIDEO_SETTINGS.BRIGHTNESS, 5) # 0 - 8
    # zed.set_camera_settings(sl.VIDEO_SETTINGS.CONTRAST, 8) # 0 - 8
    # zed.set_camera_settings(sl.VIDEO_SETTINGS.HUE, 11) # 0 - 11
    # zed.set_camera_settings(sl.VIDEO_SETTINGS.SATURATION, 8) # 0 - 8
    # zed.set_camera_settings(sl.VIDEO_SETTINGS.SHARPNESS, 8) # 0 - 8
    # zed.set_camera_settings(sl.VIDEO_SETTINGS.GAMMA, 8) # 1 - 9
    # zed.set_camera_settings(sl.VIDEO_SETTINGS.GAIN, 8) # 0 - 100
    # zed.set_camera_settings(sl.VIDEO_SETTINGS.EXPOSURE, 8) # 0 - 100
    # zed.set_camera_settings(sl.VIDEO_SETTINGS.AEC_AGC, 8) # True | False
    # zed.set_camera_settings(sl.VIDEO_SETTINGS.AEC_AGC_ROI, 8) # True | False
    # zed.set_camera_settings(sl.VIDEO_SETTINGS.WHITEBALANCE_TEMPERATURE, 8) # 2800 - 6500 (100+)
    # zed.set_camera_settings(sl.VIDEO_SETTINGS.WHITEBALANCE_AUTO, 8) # True | False
    # zed.set_camera_settings(sl.VIDEO_SETTINGS.LED_STATUS, 8) # 0 - 1

    
    print("BRIGHTNESS: {0}".format(zed.get_camera_settings(sl.VIDEO_SETTINGS.BRIGHTNESS))) # 0 - 8
    print("CONTRAST: {0}".format(zed.get_camera_settings(sl.VIDEO_SETTINGS.CONTRAST))) # 0 - 8
    print("HUE: {0}".format(zed.get_camera_settings(sl.VIDEO_SETTINGS.HUE))) # 0 - 11
    print("SATURATION: {0}".format(zed.get_camera_settings(sl.VIDEO_SETTINGS.SATURATION))) # 0 - 8
    print("SHARPNESS: {0}".format(zed.get_camera_settings(sl.VIDEO_SETTINGS.SHARPNESS))) # 0 - 8
    print("GAMMA: {0}".format(zed.get_camera_settings(sl.VIDEO_SETTINGS.GAMMA))) # 1 - 9
    print("GAIN: {0}".format(zed.get_camera_settings(sl.VIDEO_SETTINGS.GAIN))) # 0 - 100
    print("EXPOSURE: {0}".format(zed.get_camera_settings(sl.VIDEO_SETTINGS.EXPOSURE))) # 0 - 100
    print("AEC_AGC: {0}".format(zed.get_camera_settings(sl.VIDEO_SETTINGS.AEC_AGC))) # True | False
    print("AEC_AGC_ROI: {0}".format(zed.get_camera_settings(sl.VIDEO_SETTINGS.AEC_AGC_ROI))) # True | False
    print("WHITEBALANCE_TEMPERATURE: {0}".format(zed.get_camera_settings(sl.VIDEO_SETTINGS.WHITEBALANCE_TEMPERATURE))) # 2800 - 6500 (100+)
    print("WHITEBALANCE_AUTO: {0}".format(zed.get_camera_settings(sl.VIDEO_SETTINGS.WHITEBALANCE_AUTO))) # True | False
    print("LED_STATUS: {0}".format(zed.get_camera_settings(sl.VIDEO_SETTINGS.LED_STATUS))) # 0 - 1
    server.setZed(zed,sl)


    if status != sl.ERROR_CODE.SUCCESS:
        print(repr(status))
        exit()

    image_left_tmp = sl.Mat()
    image_left_tmp2 = sl.Mat()
    image_right_tmp = sl.Mat()

    print("Initialized Camera")



    # If the camera is static, uncomment the following line to have better performances and boxes sticked to the ground.
    positional_tracking_parameters = sl.PositionalTrackingParameters()
    # positional_tracking_parameters.set_as_static = True
    # positional_tracking_parameters.initial_world_transform = True

    initial_position = sl.Transform()
    initial_translation = sl.Translation()
    # initial_translation.init_vector(0,18,-75)
    initial_position.set_translation(initial_translation)
    positional_tracking_parameters.set_initial_world_transform(initial_position)

    zed.enable_positional_tracking(positional_tracking_parameters)

    obj_param = sl.ObjectDetectionParameters()
    obj_param.detection_model = sl.DETECTION_MODEL.CUSTOM_BOX_OBJECTS
    # obj_param.enable_tracking = True
    # obj_param.enable_mask_output = True
    zed.enable_object_detection(obj_param)

    objects = sl.Objects()
    obj_runtime_param = sl.ObjectDetectionRuntimeParameters()
    # obj_runtime_param.detection_confidence_threshold = 25

    # Display
    camera_infos = zed.get_camera_information()
    cam_w_pose = sl.Pose()
    

    print("Intializing Network...")

    device = select_device()
    half = device.type != 'cpu'  # half precision only supported on CUDA
    imgsz = img_size

    # Load model
    model = attempt_load(weights, device,False)  # load FP32
    bizzi = False
    stride = int(model.stride.max())  # model stride
    imgsz = check_img_size(imgsz, s=stride)  # check img_size
    if half:
        model.half()  # to FP16

    # Run inference
    if device.type != 'cpu':
        model(torch.zeros(1, 3, imgsz, imgsz).to(device).type_as(next(model.parameters())))  # run once


    timeName = ""
    timeNum = 0

    while not exit_signal:
        if zed.grab(runtime_params) == sl.ERROR_CODE.SUCCESS:
            zed.retrieve_image(image_left_tmp, sl.VIEW.LEFT)
            image_net = image_left_tmp.get_data()
            
            zed.retrieve_image(image_right_tmp, sl.VIEW.RIGHT)
            image_net_right = image_right_tmp.get_data()
            
            tempTime = str(datetime.utcnow().strftime('%H:%M:%S.%f')[:-3])[0:8]
            if timeName != tempTime:
                print("FPS: {0}".format(str(timeNum)))
                timeNum = 0
                timeName = tempTime
            timeNum = timeNum + 1

            filename = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cv2.imwrite("../../dump/photos/{0}.jpg".format(filename), image_net[:,:,:3])
            time.sleep(1)
        else:
            print("failed")
    print("done")
    zed.close()

def main():
    plot_thread = Thread(target=plt_thread, kwargs={'weights': opt.weights, 'img_size': opt.img_size, "conf_thres": opt.conf_thres})
    plot_thread.start()
    
    while bizzi:
        time.sleep(1)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--weights', nargs='+', type=str, default='best.pt', help='model.pt path(s)')
    parser.add_argument('--svo', type=str, default=None, help='optional svo file')
    parser.add_argument('--img_size', type=int, default=416, help='inference size (pixels)')
    parser.add_argument('--conf_thres', type=float, default=0.4, help='object confidence threshold')
    opt = parser.parse_args()

    with torch.no_grad():
        main()
