#!/usr/bin/env python3.8

from __future__ import division
import matplotlib.pyplot as plt

from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import math
import numpy as np
import json 

import aux
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
# fig, ax = plt.subplots()


# def toBGR(r,g,b):
#     return (b,g,r)

# colors in BGR
Cache = {
    "blue": {
        "classId": 0,
        "color": (255,0,0),
        "items": {}
    },
    "green": {
        "classId": 1,
        "color": (0,255,0),
        "items": {}
    },
    "red": {
        "classId": 2,
        "color": (0,0,255),
        "items": {}
    },
    "pink": {
        "classId": 3,
        "color": (255,0,255),
        "items": {}
    },
    "yellow": {
        "classId": 4,
        "color": (0,255,255),
        "items": {}
    },
    "self": {
        "classId": [],
        "color": (0,0,0),
        "items": {
            "0":{
                "translation":{
                    "x": 0,
                    "y": 0,
                    "z": 0,
                },
                "orientation": {
                    "x": 0,
                    "y": 0,
                    "z": 0,
                    "w": 0,
                },
                "timestamp": 0
            }
        }
    }
}
server.setCache(Cache)


def plotPylons(blue_pylons, red_pylons, image):
    plt.clf()

    # fig = plt.figure()
    # canvas = FigureCanvas(fig)

    bp = []

    if(len(blue_pylons)>1):
        x,y = aux.getXY(blue_pylons)
        # plt.plot( x,y,'o',color='blue' )
    if(len(red_pylons)>1):
        x,y = aux.getXY(red_pylons)
        # plt.plot( x,y,'o',color='red' )

    three_layer_image = image[:,:,:3]
    # canvas.draw()
    # image = np.frombuffer(fig.canvas.tostring_rgb(), dtype=np.uint8)
    # image = image.reshape(fig.canvas.get_width_height()[::-1] + (3,))

    server.sendWebsocketMessage("left-eye:"+str(aux.image_to_base64(three_layer_image)))
    # server.sendWebsocketMessage("chart:"+str(aux.image_to_base64(image)))
    server.sendWebsocketMessage("pylons:"+str(blue_pylons)+":"+str(red_pylons))
    # cv2.imwrite('../../dump/view.jpg', temp)
    plt.close()

def euler_from_quaternion(x, y, z, w):
        """
        Convert a quaternion into euler angles (roll, pitch, yaw)
        roll is rotation around x in radians (counterclockwise)
        pitch is rotation around y in radians (counterclockwise)
        yaw is rotation around z in radians (counterclockwise)
        """
        t0 = +2.0 * (w * x + y * z)
        t1 = +1.0 - 2.0 * (x * x + y * y)
        roll_x = math.atan2(t0, t1)
     
        t2 = +2.0 * (w * y - z * x)
        t2 = +1.0 if t2 > +1.0 else t2
        t2 = -1.0 if t2 < -1.0 else t2
        pitch_y = math.asin(t2)
     
        t3 = +2.0 * (w * z + x * y)
        t4 = +1.0 - 2.0 * (y * y + z * z)
        yaw_z = math.atan2(t3, t4)
     
        return roll_x, pitch_y, yaw_z # in radians


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
    # init_params.depth_mode = sl.DEPTH_MODE.ULTRA  # QUALITY
    init_params.depth_mode = sl.DEPTH_MODE.QUALITY #PERFORMANCE  # QUALITY
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

    secCache = 0

    while not exit_signal:
        if zed.grab(runtime_params) == sl.ERROR_CODE.SUCCESS:
            # Get the pose of the camera relative to the world frame
            state = zed.get_position(cam_w_pose, sl.REFERENCE_FRAME.WORLD)
            # Display translation and timestamp
            py_translation = sl.Translation()
            tx = round(cam_w_pose.get_translation(py_translation).get()[0], 3)
            ty = round(cam_w_pose.get_translation(py_translation).get()[1], 3)
            tz = round(cam_w_pose.get_translation(py_translation).get()[2], 3)
            # print("Translation: tx: {0}, ty:  {1}, tz:  {2}, timestamp: {3}".format(tx, ty, tz, cam_w_pose.timestamp.get_seconds()))
            #Display orientation quaternion
            py_orientation = sl.Orientation()
            ox = round(cam_w_pose.get_orientation(py_orientation).get()[0], 3)
            oy = round(cam_w_pose.get_orientation(py_orientation).get()[1], 3)
            oz = round(cam_w_pose.get_orientation(py_orientation).get()[2], 3)
            ow = round(cam_w_pose.get_orientation(py_orientation).get()[3], 3)
            
            ex = round(cam_w_pose.get_euler_angles()[0],3)
            ey = round(cam_w_pose.get_euler_angles()[1],3)
            ez = round(cam_w_pose.get_euler_angles()[2],3)

            vx = round(cam_w_pose.get_rotation_vector()[0],3)
            vy = round(cam_w_pose.get_rotation_vector()[1],3)
            vz = round(cam_w_pose.get_rotation_vector()[2],3)

            # print("Translation: tx: {0}, ty:  {1}, tz:  {2}, timestamp: {3} | Orientation: ox: {4}, oy:  {5}, oz: {6}, ow: {7}".format(tx, ty, tz, cam_w_pose.timestamp.get_seconds(),ox, oy, oz, ow))
            # roll_x, pitch_y, yaw_z = euler_from_quaternion(ox,oy,oz,ow)
            # (x, y, z, w):
            Cache["self"]["items"]["0"] = {
                "translation":{
                    "x": tx,
                    "y": ty,
                    "z": tz,
                },
                "orientation": {
                    "x": ox,
                    "y": oy,
                    "z": oz,
                    "w": ow,
                },
                "euler": {
                    "x": ex,
                    "y": ey,
                    "z": ez,
                },
                "rvect": {
                    "x": vx,
                    "y": vy,
                    "z": vz,
                },
                "timestamp": cam_w_pose.timestamp.get_seconds()
            }
            # json_object = json.dumps(Cache)
            # server.sendWebsocketMessage("self:"+json_object)

            zed.retrieve_image(image_left_tmp, sl.VIEW.LEFT)
            image_net = image_left_tmp.get_data()
            
            # zed.retrieve_image(image_right_tmp, sl.VIEW.RIGHT)
            # image_net_right = image_right_tmp.get_data()
            
            img, ratio, pad = aux.img_preprocess(image_net, device, half, imgsz)
            pred = model(img)[0]
            det = non_max_suppression(pred, conf_thres, iou_thres)
            detections = aux.detections_to_custom_box(det, img, image_net)
            zed.ingest_custom_box_objects(detections)
            zed.retrieve_objects(objects, obj_runtime_param)
            # if objects.is_new :
            obj_array = objects.object_list

            tempTime = str(datetime.utcnow().strftime('%H:%M:%S.%f')[:-3])[0:8]
            if timeName != tempTime:
                print("FPS: {0}".format(str(timeNum)))
                timeNum = 0
                timeName = tempTime
            timeNum = timeNum + 1

            blue_pylons = []
            red_pylons = []
            if len(obj_array) > 0:
                # print("{0} Recognized pylons: {1}".format(tempTime,str(len(obj_array))))
                
                for obj in obj_array:
                    if not math.isnan(obj.position[0]):
                        # Siehe dump/example_obj.json
                        # dic = {
                        #     "action_state": obj.action_state,
                        #     "bounding_box": obj.bounding_box,
                        #     "bounding_box_2d": obj.bounding_box_2d,
                        #     "confidence": obj.confidence,
                        #     "dimensions": obj.dimensions,
                        #     "global_root_orientation": obj.global_root_orientation,
                        #     "head_bounding_box": obj.head_bounding_box,
                        #     "head_bounding_box_2d": obj.head_bounding_box_2d,
                        #     "head_position": obj.head_position,
                        #     "id": obj.id,
                        #     "keypoint": obj.keypoint,
                        #     "keypoint_2d": obj.keypoint_2d,
                        #     "keypoint_confidence": obj.keypoint_confidence,
                        #     "label": obj.label,
                        #     "local_orientation_per_joint": obj.local_orientation_per_joint,
                        #     "local_position_per_joint": obj.local_position_per_joint,
                        #     "mask": obj.mask,
                        #     "position": obj.position,
                        #     "raw_label": obj.raw_label,
                        #     "sublabel": obj.sublabel,
                        #     "tracking_state": obj.tracking_state,
                        #     "unique_object_id": obj.unique_object_id,
                        #     "velocity": obj.velocity,
                        # }
                        # print(dic)
                        if obj.tracking_state==sl.OBJECT_TRACKING_STATE.OK:

                            color = (0,0,0)

                            # if(obj.raw_label == 0 or obj.raw_label == 1):
                            #     blue_pylons.append([obj.position[0],obj.position[2]])
                            #     color = (255,0,0)
                            # elif(obj.raw_label == 2 or obj.raw_label == 3):
                            #     red_pylons.append([obj.position[0],obj.position[2]])
                            #     color = (0,0,255)
                            # else:
                            #     print("Found pylon out of identity")
                            
                            # pylons = ["blue","green","orange","pink","yellow"]
                            def position_to_object(pos):
                                return {"x":pos[0],"y":pos[1],"z":pos[2]}
                                
                            def compare_position_and_update(old,new,limit=0.5):
                                a = np.array((old["x"],old["y"],old["z"]))
                                b = np.array((new["x"],new["y"],new["z"]))
                                dist = np.linalg.norm(a-b)
                                return old if dist > limit else new

                            key = ""

                            if(obj.raw_label == Cache["blue"]["classId"]):
                                key = "blue"
                            elif(obj.raw_label == Cache["green"]["classId"]):
                                key = "green"
                            elif(obj.raw_label == Cache["red"]["classId"]):
                                key = "red"
                            elif(obj.raw_label == Cache["pink"]["classId"]):
                                key = "pink"
                            elif(obj.raw_label == Cache["yellow"]["classId"]):
                                key = "yellow"
                            else:
                                print("Found pylon out of identity")
                                return
                            
                            
                            color = Cache[key]["color"]
                            if obj.id in Cache[key]["items"]:
                                Cache[key]["items"][obj.id] = compare_position_and_update(
                                    Cache[key]["items"][obj.id],
                                    position_to_object(obj.position)
                                )
                            else:
                                Cache[key]["items"][obj.id] = position_to_object(obj.position)
                            
                            font = cv2.FONT_HERSHEY_SIMPLEX
                            org = (int(obj.bounding_box_2d[0][0]),int(obj.bounding_box_2d[0][1]))
                            fontScale = .5
                            thickness = 1
                            image_net = cv2.putText(image_net, "(id: {2} | class: {3}) {0} x {1}".format(
                                round(obj.position[0]-30),
                                round(obj.position[2]),
                                obj.id,
                                key
                            ), org, font, fontScale, color, thickness, cv2.LINE_AA)
                            # print("draw")
                            cv2.line(image_net, (int(obj.bounding_box_2d[0][0]),int(obj.bounding_box_2d[0][1])),(int(obj.bounding_box_2d[1][0]),int(obj.bounding_box_2d[1][1])), color, 1) 
                            cv2.line(image_net, (int(obj.bounding_box_2d[1][0]),int(obj.bounding_box_2d[1][1])),(int(obj.bounding_box_2d[2][0]),int(obj.bounding_box_2d[2][1])), color, 1) 
                            cv2.line(image_net, (int(obj.bounding_box_2d[2][0]),int(obj.bounding_box_2d[2][1])),(int(obj.bounding_box_2d[3][0]),int(obj.bounding_box_2d[3][1])), color, 1) 
                            cv2.line(image_net, (int(obj.bounding_box_2d[3][0]),int(obj.bounding_box_2d[3][1])),(int(obj.bounding_box_2d[0][0]),int(obj.bounding_box_2d[0][1])), color, 1) 

                # print("show")

                json_object = json.dumps(Cache)
                server.setImage(image_net[:,:,:3])
                now = datetime.now()
                if secCache != now.second:
                    secCache  = now.second
                    server.sendWebsocketMessage("left-eye:"+str(aux.image_to_base64(image_net[:,:,:3])))
                # server.sendWebsocketMessage("chart:"+str(aux.image_to_base64(image)))
                server.setPositions(json_object)
                # server.sendWebsocketMessage("pylons:"+json_object)
                # else:
                #     plotPylons([], [],image_net)
        else:
            print("failed")
    print("done")

    zed.close()

def main():
    # capture_thread = Thread(target=torch_thread, kwargs={'weights': opt.weights, 'img_size': opt.img_size, "conf_thres": opt.conf_thres})
    # capture_thread.start()

    # plt_thread()
    plot_thread = Thread(target=plt_thread, kwargs={'weights': opt.weights, 'img_size': opt.img_size, "conf_thres": opt.conf_thres})
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
