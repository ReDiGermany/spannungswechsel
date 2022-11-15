#!/usr/bin/env python3.8

from __future__ import division
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from scipy import interpolate

import tkinter

import math

import sys
import numpy as np

import time

import argparse
import torch
import cv2
import pyzed.sl as sl
import torch.backends.cudnn as cudnn

sys.path.insert(0, './yolov5')
from models.experimental import attempt_load
from utils.general import check_img_size, non_max_suppression, scale_boxes, xyxy2xywh
from utils.torch_utils import select_device
from utils.augmentations import letterbox

from threading import Lock, Thread
from time import sleep

import ogl_viewer.viewer as gl
import cv_viewer.tracking_viewer as cv_viewer

lock = Lock()
run_signal = False
exit_signal = False

pylons = ["blue","green","orange","pink","yellow"]

global_x = []
global_y = []
global_xnew = []
global_ynew = []


global_x1 = []
global_y1 = []
global_x1new = []
global_y1new = []

def img_preprocess(img, device, half, net_size):
    net_image, ratio, pad = letterbox(img[:, :, :3], net_size, auto=False)
    net_image = net_image.transpose((2, 0, 1))[::-1]  # HWC to CHW, BGR to RGB
    net_image = np.ascontiguousarray(net_image)

    img = torch.from_numpy(net_image).to(device)
    img = img.half() if half else img.float()  # uint8 to fp16/32
    img /= 255.0  # 0 - 255 to 0.0 - 1.0

    if img.ndimension() == 3:
        img = img.unsqueeze(0)
    return img, ratio, pad


def plotCircle(nodes):
    x = nodes[:,0]
    y = nodes[:,1]

    tck,u     = interpolate.splprep( [x,y] ,s = 0) #,per=True 
    xnew,ynew = interpolate.splev( np.linspace( 0, 1, 100 ), tck,der = 0)

    return [x,y,xnew,ynew]
    # plt.plot( x,y,'o' , xnew ,ynew )


def plotSplines(pylons_left, pylons_right):
    global global_x1, global_y1, global_x1new, global_y1new, global_x, global_y, global_xnew, global_ynew
    print(pylons_left)
    print(pylons_right)
    plt.clf()
    #plt.switch_backend('TkAgg')
    if(len(pylons_left)>1):
        nodes_left = np.array(pylons_left)
        x = nodes_left[:,0]
        y = nodes_left[:,1]
        #x,y,xnew,ynew = plotCircle(nodes_left)

        #plt.plot( x,y,'o' , xnew ,ynew )
        plt.plot( x,y,'o',color='blue' )
    if(len(pylons_right)>1):
        nodes_right = np.array(pylons_right)
        x = nodes_right[:,0]
        y = nodes_right[:,1]
        #x,y,xnew,ynew = plotCircle(nodes_right) 

        #plt.plot( x,y,'p' , xnew ,ynew )
        plt.plot( x,y,'o',color='red' )

        
    #nodes = np.array([
    #    [1,4],
    #    [1,6],
    #    [2,7],
    #    [3,6],
    #    [3,5.5],
    #    [2,4.5],
    #    [2,3.5],
    #    [3,2.5],
    #    [3,2],
    #    [2,1],
    #    [1,2],
    #    [1,4],
    #])
    #x,y,xnew,ynew = plotCircle(nodes)
    #plt.plot( x,y,'o' , xnew ,ynew )
    # plt.rcParams["figure.figsize"] = [np.max(x)+1, np.max(y)+1]
    # plt.rcParams["figure.autolayout"] = True
    # max = np.max(x)
    # if np.max(x)<np.max(y):
    #     max = np.max(y)
    # plt.xlim(-1, max+2)
    # plt.ylim(-1, max+2)

    # plt.show()
    plt.savefig("mygraph.png")


def xywh2abcd(xywh, im_shape):
    output = np.zeros((4, 2))

    # Center / Width / Height -> BBox corners coordinates
    x_min = (xywh[0] - 0.5*xywh[2]) * im_shape[1]
    x_max = (xywh[0] + 0.5*xywh[2]) * im_shape[1]
    y_min = (xywh[1] - 0.5*xywh[3]) * im_shape[0]
    y_max = (xywh[1] + 0.5*xywh[3]) * im_shape[0]

    # A ------ B
    # | Object |
    # D ------ C

    output[0][0] = x_min
    output[0][1] = y_min

    output[1][0] = x_max
    output[1][1] = y_min

    output[2][0] = x_min
    output[2][1] = y_max

    output[3][0] = x_max
    output[3][1] = y_max
    return output


def detections_to_custom_box(detections, im, im0):
    output = []
    for i, det in enumerate(detections):
        if len(det):
            det[:, :4] = scale_boxes(im.shape[2:], det[:, :4], im0.shape).round()
            gn = torch.tensor(im0.shape)[[1, 0, 1, 0]]  # normalization gain whwh

            for *xyxy, conf, cls in reversed(det):
                xywh = (xyxy2xywh(torch.tensor(xyxy).view(1, 4)) / gn).view(-1).tolist()  # normalized xywh

                # Creating ingestable objects for the ZED SDK
                obj = sl.CustomBoxObjectData()
                obj.bounding_box_2d = xywh2abcd(xywh, im0.shape)
                obj.label = cls
                obj.probability = conf
                obj.is_grounded = False
                output.append(obj)
    return output


bizzi = True

def torch_thread(weights, img_size, conf_thres=0.2, iou_thres=0.45):
    global image_net, exit_signal, run_signal, detections, bizzi

    print("Intializing Network...")

    device = select_device()
    half = device.type != 'cpu'  # half precision only supported on CUDA
    imgsz = img_size


    # Load model
    # TODO: attempt_load kills matplot!
    model = attempt_load(weights, device,False)  # load FP32
    bizzi = False
    stride = int(model.stride.max())  # model stride
    imgsz = check_img_size(imgsz, s=stride)  # check img_size
    if half:
        model.half()  # to FP16
    cudnn.benchmark = True

    # Run inference
    if device.type != 'cpu':
        model(torch.zeros(1, 3, imgsz, imgsz).to(device).type_as(next(model.parameters())))  # run once

    while not exit_signal:
        if run_signal:
            lock.acquire()
            img, ratio, pad = img_preprocess(image_net, device, half, imgsz)

            pred = model(img)[0]
            det = non_max_suppression(pred, conf_thres, iou_thres)

            # ZED CustomBox format (with inverse letterboxing tf applied)
            detections = detections_to_custom_box(det, img, image_net)
            lock.release()
            run_signal = False
        sleep(0.01)

#matplotlib.use("TkAgg")

fig, ax = plt.subplots()

def animate(i):
    print("lalalalallalalal")
    global global_x1, global_y1, global_x1new, global_y1new, global_x, global_y, global_xnew, global_ynew
    # pullData = open("sampleText.txt","r").read()
    # dataArray = pullData.split('\n')
    # xar = []
    # yar = []
    # for eachLine in dataArray:
    #     if len(eachLine)>1:
    #         x,y = eachLine.split(',')
    #         xar.append(int(x))
    #         yar.append(int(y))
    print("plotaaa")
    global ax1
    ax.clear()
    ax.plot( global_x,global_y,'o' , global_xnew ,global_ynew )
    ax.plot( global_x1,global_y1,'o' , global_x1new ,global_y1new )
    ax.set_ylim([0,255])


def plt_thread():
    global image_net, exit_signal, run_signal, detections
    print("Initializing Camera...")

    zed = sl.Camera()

    input_type = sl.InputType()
    if opt.svo is not None:
        input_type.set_from_svo_file(opt.svo)

    # Create a InitParameters object and set configuration parameters
    init_params = sl.InitParameters(input_t=input_type, svo_real_time_mode=True)
    init_params.camera_resolution = sl.RESOLUTION.HD720
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

    print("Initialized Camera")

    positional_tracking_parameters = sl.PositionalTrackingParameters()
    # If the camera is static, uncomment the following line to have better performances and boxes sticked to the ground.
    positional_tracking_parameters.set_as_static = True
    zed.enable_positional_tracking(positional_tracking_parameters)

    obj_param = sl.ObjectDetectionParameters()
    obj_param.detection_model = sl.DETECTION_MODEL.CUSTOM_BOX_OBJECTS
    obj_param.enable_tracking = True
    zed.enable_object_detection(obj_param)

    objects = sl.Objects()
    obj_runtime_param = sl.ObjectDetectionRuntimeParameters()

    #tracking_parameters = sl.PositionalTrackingParameters()
    #err = zed.enable_positional_tracking(tracking_parameters)

    # Display
    camera_infos = zed.get_camera_information()
    # Create OpenGL viewer
    # viewer = gl.GLViewer()
    # point_cloud_res = sl.Resolution(min(camera_infos.camera_resolution.width, 720), min(camera_infos.camera_resolution.height, 404))
# 
    # point_cloud_render = sl.Mat()
    # viewer.init(camera_infos.camera_model, point_cloud_res, obj_param.enable_tracking)
    # point_cloud = sl.Mat(point_cloud_res.width, point_cloud_res.height, sl.MAT_TYPE.F32_C4, sl.MEM.CPU)
    # image_left = sl.Mat()
    # # Utilities for 2D display
    # display_resolution = sl.Resolution(min(camera_infos.camera_resolution.width, 1280), min(camera_infos.camera_resolution.height, 720))
    # image_scale = [display_resolution.width / camera_infos.camera_resolution.width, display_resolution.height / camera_infos.camera_resolution.height]
    # image_left_ocv = np.full((display_resolution.height, display_resolution.width, 4), [245, 239, 239, 255], np.uint8)
# 
    # # Utilities for tracks view
    # camera_config = zed.get_camera_information().camera_configuration
    # tracks_resolution = sl.Resolution(400, display_resolution.height)
    # track_view_generator = cv_viewer.TrackingViewer(tracks_resolution, camera_config.camera_fps,
    #                                                 init_params.depth_maximum_distance)
    # track_view_generator.set_camera_calibration(camera_config.calibration_parameters)
    # image_track_ocv = np.zeros((tracks_resolution.height, tracks_resolution.width, 4), np.uint8)
    # Camera pose
    cam_w_pose = sl.Pose()
    print("?")
    while not exit_signal:
        if zed.grab(runtime_params) == sl.ERROR_CODE.SUCCESS:
            # -- Get the image
            lock.acquire()
            zed.retrieve_image(image_left_tmp, sl.VIEW.LEFT)
            image_net = image_left_tmp.get_data()
            lock.release()
            run_signal = True

            # -- Detection running on the other thread
            while run_signal:
                sleep(0.001)

            # Wait for detections
            lock.acquire()
            # -- Ingest detections
            zed.ingest_custom_box_objects(detections)
            lock.release()
            zed.retrieve_objects(objects, obj_runtime_param)
            if objects.is_new :
                obj_array = objects.object_list
            #print(str(len(obj_array))+" Object(s) detected\n")
            left_pylons = []
            right_pylons = []
            if len(obj_array) > 0:
                print(len(obj_array))
                for obj in obj_array:
                    if not math.isnan(obj.position[0]):
                        if(obj.raw_label == 0 or obj.raw_label == 1):
                            left_pylons.append([obj.position[0],obj.position[1]])
                        if(obj.raw_label == 2 or obj.raw_label == 3):
                            right_pylons.append([obj.position[0],obj.position[1]])
                # print(arr)
                plotSplines(left_pylons, right_pylons)
            #print(str(len(obj_array))+" Object(s) detected\n")
                # # t = time.localtime()
                # # current_time = time.strftime("%H:%M:%S", t)
                # first_object = obj_array[0]
                # zed_pose = sl.Pose()
                # # print("First object attributes:")
                # # print(dir(first_object))
                # print("Label '"+pylons[int(repr(first_object.raw_label))]+"' ("+repr(first_object.raw_label)+") (conf. "+str(int(first_object.confidence))+"/100)")
                # if obj_param.enable_tracking :
                #     print(" Tracking ID: "+str(int(first_object.id))+" tracking state: "+repr(first_object.tracking_state)+" / "+repr(first_object.action_state)+" @ "+str(time.time()))
                # position = first_object.position
                # velocity = first_object.velocity
                # dimensions = first_object.dimensions
                # # print(str(time.time()))
                # print(" 3D position: [{0},{1},{2}]".format(position[0],position[1],position[2]))
                # #if zed.grab(runtime_parameters) == SUCCESS :
                # if True:
                #     # Get the pose of the camera relative to the world frame
                #     state = zed.get_position(zed_pose, sl.REFERENCE_FRAME.WORLD)
                #     # Display translation and timestamp
                #     py_translation = sl.Translation()
                #     # tx = round(zed_pose.get_translation(py_translation).get()[0], 3)
                #     pos = np.subtract(zed_pose.get_translation(py_translation).get(),position)
                #     if pos[0] > 0:
                #         print("left @ "+str(round(pos[2],2)))
                #     else:
                #         print("right @ "+str(round(pos[2],2)))
                # #print(np.subtract(zed.get_postition(cam_w_pose, sl.REFERENCE_FRAME.WORLD),position))
                # # print(" 3D position: [{0},{1},{2}]\n Velocity: [{3},{4},{5}]\n 3D dimentions: [{6},{7},{8}]".format(position[0],position[1],position[2],velocity[0],velocity[1],velocity[2],dimensions[0],dimensions[1],dimensions[2]))



            # # -- Display
            # # Retrieve display data
            # zed.retrieve_measure(point_cloud, sl.MEASURE.XYZRGBA, sl.MEM.CPU, point_cloud_res)
            # point_cloud.copy_to(point_cloud_render)
            # zed.retrieve_image(image_left, sl.VIEW.LEFT, sl.MEM.CPU, display_resolution)
            # zed.get_position(cam_w_pose, sl.REFERENCE_FRAME.WORLD)
# 
            # # 3D rendering
            # viewer.updateData(point_cloud_render, objects)
            # # 2D rendering
            # np.copyto(image_left_ocv, image_left.get_data())
            # cv_viewer.render_2D(image_left_ocv, image_scale, objects, obj_param.enable_tracking)
            # global_image = cv2.hconcat([image_left_ocv])
            # # Tracking view
            # track_view_generator.generate_view(objects, cam_w_pose, image_track_ocv, objects.is_tracked)
# 
            # cv2.imshow("ZED | 2D View and Birds View", global_image)
            # key = cv2.waitKey(10)
            # if key == 27:
                # exit_signal = True
        else:
            print("failed")
            #exit_signal = True
    # viewer.exit()
    print("done")

    #exit_signal = True
    zed.close()

def main():
    global ani
    ani = "aniiiii"
    # print("main()")
    # 
    capture_thread = Thread(target=torch_thread, kwargs={'weights': opt.weights, 'img_size': opt.img_size, "conf_thres": opt.conf_thres})
    capture_thread.start()
    # print("capture_thread")
# 
    # plt_thread()

    plot_thread = Thread(target=plt_thread)
    plot_thread.start()
    while bizzi:
        print("wait")
        time.sleep(1)
    #ani = animation.FuncAnimation(fig, animate, interval=1000)
    time.sleep(1)

    #matplotlib.pyplot.plot( [1,1,1],[4,2,3],'o')
    #plt.show()
    # print("plot_thread")
# 
    #print("plt.hide")
# 
    # print("ani")

    # capture_thread.join()
    # plot_thread.join()

    # plot_thread.join()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--weights', nargs='+', type=str, default='best.pt', help='model.pt path(s)')
    parser.add_argument('--svo', type=str, default=None, help='optional svo file')
    parser.add_argument('--img_size', type=int, default=416, help='inference size (pixels)')
    parser.add_argument('--conf_thres', type=float, default=0.4, help='object confidence threshold')
    opt = parser.parse_args()

    with torch.no_grad():
        main()
