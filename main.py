#!/usr/bin/env python3.8

from __future__ import division
import matplotlib.pyplot as plt

from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import math
import numpy as np
import json 
import sys

sys.path.insert(0, './car')
from nearest_neighbour import nearest_neighbour
sys.path.insert(0, './car/detector')
import aux
import server

import argparse
import torch
import cv2
import pyzed.sl as sl

from threading import Lock, Thread
import time
from datetime import datetime

sys.path.insert(0, './yolov5')
from models.experimental import attempt_load
from utils.general import check_img_size, non_max_suppression
from utils.torch_utils import select_device

lock = Lock()
run_signal = False
exit_signal = False

pylons = ["blue","green","orange","pink","yellow"]

bizzi = True

# colors in BGR


class SpannungsWechsel(Thread):                   
    # def __init__(self, weights, img_size, conf_thres=0.2, iou_thres=0.45):
    def __init__(self, group=None, target=None, name=None, args=(), kwargs=None):
        super(SpannungsWechsel,self).__init__(group=group, target=target, name=name)
        print("Init")
        self.weights = kwargs["weights"]
        self.img_size = kwargs["img_size"]
        self.conf_thres = 0.2
        self.iou_thres = 0.45
        self.image_net = []
        self.exit_signal = False
        self.run_signal = True
        self.detections = []
        self.Cache = {
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
        self.zed = None
        self.input_type = None
        self.runtime_params = None
        self.status = None
        self.image_left_tmp = sl.Mat()
        self.timeName = ""
        self.timeNum = 0
        self.secCache = 0
        self.objects = None
        self.obj_runtime_param = None
        self.cam_w_pose = None
        self.device = None
        self.half = None
        self.imgsz = None
        self.model = None
        server.setCache(self.Cache)
        print(".Init")

    def init_camera_params(self):
        # Create a InitParameters object and set configuration parameters
        init_params = sl.InitParameters(input_t=self.input_type, svo_real_time_mode=True)
        init_params.camera_resolution = sl.RESOLUTION.HD1080
        init_params.coordinate_units = sl.UNIT.CENTIMETER
        init_params.coordinate_system = sl.COORDINATE_SYSTEM.LEFT_HANDED_Y_UP
        # init_params.depth_mode = sl.DEPTH_MODE.ULTRA  # QUALITY
        init_params.depth_mode = sl.DEPTH_MODE.QUALITY #PERFORMANCE  # QUALITY
        # init_params.depth_maximum_distance = 20

        self.runtime_params = sl.RuntimeParameters()
        self.status = self.zed.open(init_params)

    def print_camera_settings(self):
        # self.zed.set_camera_settings(sl.VIDEO_SETTINGS.BRIGHTNESS, 5) # 0 - 8
        # self.zed.set_camera_settings(sl.VIDEO_SETTINGS.CONTRAST, 8) # 0 - 8
        # self.zed.set_camera_settings(sl.VIDEO_SETTINGS.HUE, 11) # 0 - 11
        # self.zed.set_camera_settings(sl.VIDEO_SETTINGS.SATURATION, 8) # 0 - 8
        # self.zed.set_camera_settings(sl.VIDEO_SETTINGS.SHARPNESS, 8) # 0 - 8
        # self.zed.set_camera_settings(sl.VIDEO_SETTINGS.GAMMA, 8) # 1 - 9
        # self.zed.set_camera_settings(sl.VIDEO_SETTINGS.GAIN, 8) # 0 - 100
        # self.zed.set_camera_settings(sl.VIDEO_SETTINGS.EXPOSURE, 8) # 0 - 100
        # self.zed.set_camera_settings(sl.VIDEO_SETTINGS.AEC_AGC, 8) # True | False
        # self.zed.set_camera_settings(sl.VIDEO_SETTINGS.AEC_AGC_ROI, 8) # True | False
        # self.zed.set_camera_settings(sl.VIDEO_SETTINGS.WHITEBALANCE_TEMPERATURE, 8) # 2800 - 6500 (100+)
        # self.zed.set_camera_settings(sl.VIDEO_SETTINGS.WHITEBALANCE_AUTO, 8) # True | False
        # self.zed.set_camera_settings(sl.VIDEO_SETTINGS.LED_STATUS, 8) # 0 - 1

        
        print("BRIGHTNESS: {0}".format(self.zed.get_camera_settings(sl.VIDEO_SETTINGS.BRIGHTNESS))) # 0 - 8
        print("CONTRAST: {0}".format(self.zed.get_camera_settings(sl.VIDEO_SETTINGS.CONTRAST))) # 0 - 8
        print("HUE: {0}".format(self.zed.get_camera_settings(sl.VIDEO_SETTINGS.HUE))) # 0 - 11
        print("SATURATION: {0}".format(self.zed.get_camera_settings(sl.VIDEO_SETTINGS.SATURATION))) # 0 - 8
        print("SHARPNESS: {0}".format(self.zed.get_camera_settings(sl.VIDEO_SETTINGS.SHARPNESS))) # 0 - 8
        print("GAMMA: {0}".format(self.zed.get_camera_settings(sl.VIDEO_SETTINGS.GAMMA))) # 1 - 9
        print("GAIN: {0}".format(self.zed.get_camera_settings(sl.VIDEO_SETTINGS.GAIN))) # 0 - 100
        print("EXPOSURE: {0}".format(self.zed.get_camera_settings(sl.VIDEO_SETTINGS.EXPOSURE))) # 0 - 100
        print("AEC_AGC: {0}".format(self.zed.get_camera_settings(sl.VIDEO_SETTINGS.AEC_AGC))) # True | False
        print("AEC_AGC_ROI: {0}".format(self.zed.get_camera_settings(sl.VIDEO_SETTINGS.AEC_AGC_ROI))) # True | False
        print("WHITEBALANCE_TEMPERATURE: {0}".format(self.zed.get_camera_settings(sl.VIDEO_SETTINGS.WHITEBALANCE_TEMPERATURE))) # 2800 - 6500 (100+)
        print("WHITEBALANCE_AUTO: {0}".format(self.zed.get_camera_settings(sl.VIDEO_SETTINGS.WHITEBALANCE_AUTO))) # True | False
        print("LED_STATUS: {0}".format(self.zed.get_camera_settings(sl.VIDEO_SETTINGS.LED_STATUS))) # 0 - 1

    def create_camera_instance(self):
        self.zed = sl.Camera()
        self.input_type = sl.InputType()
        if opt.svo is not None:
            self.input_type.set_from_svo_file(opt.svo)

    def activate_camera_tracking(self):
        # If the camera is static, uncomment the following line to have better performances and boxes sticked to the ground.
        positional_tracking_parameters = sl.PositionalTrackingParameters()
        # positional_tracking_parameters.set_as_static = True
        # positional_tracking_parameters.initial_world_transform = True

        initial_position = sl.Transform()
        initial_translation = sl.Translation()
        # initial_translation.init_vector(0,18,-75)
        initial_position.set_translation(initial_translation)
        positional_tracking_parameters.set_initial_world_transform(initial_position)

        self.zed.enable_positional_tracking(positional_tracking_parameters)

    def activate_camera_object_detection(self):
        obj_param = sl.ObjectDetectionParameters()
        obj_param.detection_model = sl.DETECTION_MODEL.CUSTOM_BOX_OBJECTS
        # obj_param.enable_tracking = True
        # obj_param.enable_mask_output = True
        self.zed.enable_object_detection(obj_param)

        self.objects = sl.Objects()
        self.obj_runtime_param = sl.ObjectDetectionRuntimeParameters()
        # obj_runtime_param.detection_confidence_threshold = 25

    def load_model(self):
        self.device = select_device()
        self.half = self.device.type != 'cpu'  # self.half precision only supported on CUDA
        self.imgsz = self.img_size

        # Load model
        self.model = attempt_load(self.weights, self.device,False)  # load FP32
        bizzi = False
        stride = int(self.model.stride.max())  # self.model stride
        self.imgsz = check_img_size(self.imgsz, s=stride)  # check self.img_size
        if self.half:
            self.model.half()  # to FP16

        # Run inference
        if self.device.type != 'cpu':
            self.model(torch.zeros(1, 3, self.imgsz, self.imgsz).to(self.device).type_as(next(self.model.parameters())))  # run once

    def update_own_position(self):
        # Get the pose of the camera relative to the world frame
        state = self.zed.get_position(self.cam_w_pose, sl.REFERENCE_FRAME.WORLD)
        # Display translation and timestamp
        py_translation = sl.Translation()
        tx = round(self.cam_w_pose.get_translation(py_translation).get()[0], 3)
        ty = round(self.cam_w_pose.get_translation(py_translation).get()[1], 3)
        tz = round(self.cam_w_pose.get_translation(py_translation).get()[2], 3)
        # print("Translation: tx: {0}, ty:  {1}, tz:  {2}, timestamp: {3}".format(tx, ty, tz, self.cam_w_pose.timestamp.get_seconds()))
        #Display orientation quaternion
        py_orientation = sl.Orientation()
        ox = round(self.cam_w_pose.get_orientation(py_orientation).get()[0], 3)
        oy = round(self.cam_w_pose.get_orientation(py_orientation).get()[1], 3)
        oz = round(self.cam_w_pose.get_orientation(py_orientation).get()[2], 3)
        ow = round(self.cam_w_pose.get_orientation(py_orientation).get()[3], 3)
        
        ex = round(self.cam_w_pose.get_euler_angles()[0],3)
        ey = round(self.cam_w_pose.get_euler_angles()[1],3)
        ez = round(self.cam_w_pose.get_euler_angles()[2],3)

        vx = round(self.cam_w_pose.get_rotation_vector()[0],3)
        vy = round(self.cam_w_pose.get_rotation_vector()[1],3)
        vz = round(self.cam_w_pose.get_rotation_vector()[2],3)

        # print("Translation: tx: {0}, ty:  {1}, tz:  {2}, timestamp: {3} | Orientation: ox: {4}, oy:  {5}, oz: {6}, ow: {7}".format(tx, ty, tz, self.cam_w_pose.timestamp.get_seconds(),ox, oy, oz, ow))
        # roll_x, pitch_y, yaw_z = euler_from_quaternion(ox,oy,oz,ow)
        # (x, y, z, w):
        self.Cache["self"]["items"]["0"] = {
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
            "timestamp": self.cam_w_pose.timestamp.get_seconds()
        }

    def position_to_object(self,pos):
        return {"x":pos[0],"y":pos[1],"z":pos[2]}
        
    def compare_position_and_update(self,old,new,limit=0.5):
        a = np.array((old["x"],old["y"],old["z"]))
        b = np.array((new["x"],new["y"],new["z"]))
        dist = np.linalg.norm(a-b)
        return old if dist > limit else new

    def add_label(self,obj,name):
        font = cv2.FONT_HERSHEY_SIMPLEX
        org = (int(obj.bounding_box_2d[0][0]),int(obj.bounding_box_2d[0][1])-10)
        org2 = (int(obj.bounding_box_2d[0][0])+1,int(obj.bounding_box_2d[0][1])-9)
        fontScale = .5
        thickness = 2
        text = "({2} {3}) {0} x {1}".format(
            round(obj.position[0]),
            round(obj.position[2]),
            obj.id,
            name[0]
        )
        self.image_net = cv2.putText(self.image_net, text, org, font, fontScale, (0,0,0), 10, cv2.LINE_AA)
        self.image_net = cv2.putText(self.image_net, text, org, font, fontScale, (255,255,255), 1, cv2.LINE_AA)
        
        thickness = 1
        image = cv2.rectangle(self.image_net, (int(obj.bounding_box_2d[0][0]),int(obj.bounding_box_2d[0][1])), (int(obj.bounding_box_2d[2][0]),int(obj.bounding_box_2d[2][1])), self.Cache[name]["color"], thickness)

    def check_item(self,obj):
        if obj.tracking_state==sl.OBJECT_TRACKING_STATE.OK:

            color = (0,0,0)

            key = ""

            if(obj.raw_label == self.Cache["blue"]["classId"]): key = "blue"
            elif(obj.raw_label == self.Cache["green"]["classId"]): key = "green"
            elif(obj.raw_label == self.Cache["red"]["classId"]): key = "red"
            elif(obj.raw_label == self.Cache["pink"]["classId"]): key = "pink"
            elif(obj.raw_label == self.Cache["yellow"]["classId"]): key = "yellow"
            else:
                print("Found pylon out of identity")
                return
            
            color = self.Cache[key]["color"]
            if obj.id in self.Cache[key]["items"]:
                self.Cache[key]["items"][obj.id] = self.compare_position_and_update(
                    self.Cache[key]["items"][obj.id],
                    self.position_to_object(obj.position)
                )
            else:
                self.Cache[key]["items"][obj.id] = self.position_to_object(obj.position)
            self.add_label(obj,key)

    def process_image(self):
        self.update_own_position()

        self.zed.retrieve_image(self.image_left_tmp, sl.VIEW.LEFT)
        self.image_net = self.image_left_tmp.get_data()
        
        
        img, ratio, pad = aux.img_preprocess(self.image_net, self.device, self.half, self.imgsz)
        pred = self.model(img)[0]
        det = non_max_suppression(pred, self.conf_thres, self.iou_thres)
        detections = aux.detections_to_custom_box(det, img, self.image_net)
        self.zed.ingest_custom_box_objects(detections)
        self.zed.retrieve_objects(self.objects, self.obj_runtime_param)
        # if self.objects.is_new :
        obj_array = self.objects.object_list

        tempTime = str(datetime.utcnow().strftime('%H:%M:%S.%f')[:-3])[0:8]
        if self.timeName != tempTime:
            print("FPS: {0}".format(str(self.timeNum)))
            self.timeNum = 0
            self.timeName = tempTime
        self.timeNum = self.timeNum + 1

        if len(obj_array) > 0:
            for obj in obj_array:
                if not math.isnan(obj.position[0]):
                    # print(obj.position)
                    self.check_item(obj)

            temp_pylons = []

            def copy_item(item,i,cls):
                # print(item)
                return {"x":item["x"],"y":item["z"],"color":cls,"id":str(i)}

            for item in self.Cache["blue"]["items"]:
                temp_pylons.append(copy_item(self.Cache["blue"]["items"][item],item,"blue"))

            for item in self.Cache["green"]["items"]:
                temp_pylons.append(copy_item(self.Cache["green"]["items"][item],item,"blue"))

            for item in self.Cache["red"]["items"]:
                temp_pylons.append(copy_item(self.Cache["red"]["items"][item],item,"red"))

            for item in self.Cache["pink"]["items"]:
                temp_pylons.append(copy_item(self.Cache["pink"]["items"][item],item,"red"))

            # print(temp_pylons)

            route = None
            neighbours = None
            curve = None
            pylons = None
            blue_curved = None
            red_curved = None


            if(len(temp_pylons)):
                route,neighbours,curve,pylons,blue_curved,red_curved = nearest_neighbour(temp_pylons,False)

            # json_object = json.dumps(self.Cache)
            json_object = json.dumps({
                "neighbours": neighbours,
                "route": route,
                "curve": curve,
                "pylons": pylons,
                "blueCurved": blue_curved,
                "redCurved": red_curved,
            })
            server.setImage(self.image_net[:,:,:3])
            now = datetime.now()
            if self.secCache != now.second:
                self.secCache  = now.second
                server.sendWebsocketMessage("left-eye:"+str(aux.image_to_base64(self.image_net[:,:,:3])))
            # server.sendWebsocketMessage("chart:"+str(aux.image_to_base64(image)))
            server.setPositions(json_object)
            # server.sendWebsocketMessage("pylons:"+json_object)
            # else:

    def run(self):
        print("Initializing Camera...")

        self.create_camera_instance()
        self.init_camera_params()
        # self.print_camera_settings()
        server.setZed(self.zed,sl)

        if self.status != sl.ERROR_CODE.SUCCESS:
            print(repr(status))
            exit()

        print("Initialized Camera")

        self.activate_camera_tracking()
        self.activate_camera_object_detection()
        self.cam_w_pose = sl.Pose()
        
        print("Intializing Network...")

        self.load_model()

        while not exit_signal:
            if self.zed.grab(self.runtime_params) == sl.ERROR_CODE.SUCCESS:
                self.process_image()
            else:
                print("failed")
        print("done")

        zed.close()
        
def main():
    plot_thread = SpannungsWechsel(kwargs={'weights': opt.weights, 'img_size': opt.img_size, "conf_thres": opt.conf_thres})
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
