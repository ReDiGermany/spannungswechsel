#!/usr/bin/env python3.8

from __future__ import division
import matplotlib.pyplot as plt

from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import math
import numpy as np

import aux
import server

import argparse
import torch
import cv2
import pyzed.sl as sl

from threading import Lock, Thread
import time

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
fig, ax = plt.subplots()

def plotPylons(blue_pylons, red_pylons, image):
    # print(blue_pylons)
    # print(red_pylons)
    plt.clf()

    fig = plt.figure()
    canvas = FigureCanvas(fig)
    ax = fig.gca()
    
    if(len(blue_pylons)>1):
        x,y = aux.getXY(blue_pylons)
        plt.plot( x,y,'o',color='blue' )
    if(len(red_pylons)>1):
        x,y = aux.getXY(red_pylons)
        plt.plot( x,y,'o',color='red' )

    width, height = fig.get_size_inches() * fig.get_dpi()
    canvas.draw()
    three_layer_image = image[:,:,:3]
    image = np.frombuffer(fig.canvas.tostring_rgb(), dtype=np.uint8)
    image = image.reshape(fig.canvas.get_width_height()[::-1] + (3,))

    temp = aux.merge_image(three_layer_image,image,1920 - int(680/2),0)
    server.sendWebsocketMessage(aux.image_to_base64(temp))
    # cv2.imwrite('../../dump/view.jpg', temp)
    plt.close()


def torch_thread(weights, img_size, conf_thres=0.2, iou_thres=0.45):
    global image_net, exit_signal, run_signal, detections, bizzi

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

    while not exit_signal:
        if run_signal:
            lock.acquire()
            img, ratio, pad = aux.img_preprocess(image_net, device, half, imgsz)

            pred = model(img)[0]
            det = non_max_suppression(pred, conf_thres, iou_thres)

            # ZED CustomBox format (with inverse letterboxing tf applied)
            detections = aux.detections_to_custom_box(det, img, image_net)
            lock.release()
            run_signal = False
        time.sleep(0.01)

def plt_thread():
    global image_net, exit_signal, run_signal, detections
    print("Initializing Camera...")

    zed = sl.Camera()

    input_type = sl.InputType()
    if opt.svo is not None:
        input_type.set_from_svo_file(opt.svo)

    # Create a InitParameters object and set configuration parameters
    init_params = sl.InitParameters(input_t=input_type, svo_real_time_mode=True)
    init_params.camera_resolution = sl.RESOLUTION.HD1080
    init_params.coordinate_units = sl.UNIT.METER
    init_params.depth_mode = sl.DEPTH_MODE.ULTRA  # QUALITY
    init_params.coordinate_system = sl.COORDINATE_SYSTEM.RIGHT_HANDED_Y_UP
    init_params.depth_maximum_distance = 20

    runtime_params = sl.RuntimeParameters()
    status = zed.open(init_params)

    if status != sl.ERROR_CODE.SUCCESS:
        print(repr(status))
        exit()

    image_left_tmp = sl.Mat()
    image_left_tmp2 = sl.Mat()
    image_right_tmp = sl.Mat()

    print("Initialized Camera")

    positional_tracking_parameters = sl.PositionalTrackingParameters()
    # If the camera is static, uncomment the following line to have better performances and boxes sticked to the ground.
    positional_tracking_parameters.set_as_static = True
    zed.enable_positional_tracking(positional_tracking_parameters)

    obj_param = sl.ObjectDetectionParameters()
    obj_param.detection_model = sl.DETECTION_MODEL.CUSTOM_BOX_OBJECTS
    obj_param.enable_tracking = True
    obj_param.enable_mask_output = True
    zed.enable_object_detection(obj_param)

    objects = sl.Objects()
    obj_runtime_param = sl.ObjectDetectionRuntimeParameters()

    # Display
    camera_infos = zed.get_camera_information()
    cam_w_pose = sl.Pose()
    print("?")
    while not exit_signal:
        if zed.grab(runtime_params) == sl.ERROR_CODE.SUCCESS:
            # -- Get the image
            lock.acquire()
            zed.retrieve_image(image_left_tmp, sl.VIEW.LEFT)
            image_net = image_left_tmp.get_data()
            zed.retrieve_image(image_right_tmp, sl.VIEW.RIGHT)
            image_net_right = image_right_tmp.get_data()
            lock.release()
            run_signal = True

            # -- Detection running on the other thread
            while run_signal:
                time.sleep(0.001)

            # Wait for detections
            lock.acquire()
            # -- Ingest detections
            zed.ingest_custom_box_objects(detections)
            lock.release()
            zed.retrieve_objects(objects, obj_runtime_param)
            if objects.is_new :
                obj_array = objects.object_list

            # zed.retrieve_image(image_left_tmp2, sl.VIEW.LEFT)
            # vis1 = np.concatenate((image_left_tmp2, image_net), axis=1)
            blue_pylons = []
            red_pylons = []
            if len(obj_array) > 0:
                print("{0} Recognized pylons: {1}".format(time.strftime("%H:%M:%S",time.localtime()),str(len(obj_array))))
                
                for obj in obj_array:
                    if not math.isnan(obj.position[0]):
                        if(obj.raw_label == 0 or obj.raw_label == 1):
                            blue_pylons.append([obj.position[0],obj.position[1]])
                        elif(obj.raw_label == 2 or obj.raw_label == 3):
                            red_pylons.append([obj.position[0],obj.position[1]])
                        else:
                            print("Found pylon out of identity")
                    else:
                        print("Found unpositioned item")
                vis = np.concatenate((image_net, image_net_right), axis=1)
                plotPylons(blue_pylons, red_pylons,vis)
        else:
            print("failed")
    print("done")

    zed.close()

def main():
    capture_thread = Thread(target=torch_thread, kwargs={'weights': opt.weights, 'img_size': opt.img_size, "conf_thres": opt.conf_thres})
    capture_thread.start()
    plot_thread = Thread(target=plt_thread)
    plot_thread.start()
    server.startServers()
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
