#!/usr/bin/python3.8
print("Welcome!")
from simple_websocket_server import WebSocketServer, WebSocket
from http.server import BaseHTTPRequestHandler, HTTPServer
import http.server
import time
import threading
import netifaces as ni
import numpy as np
from PIL import Image
import cv2
import io
from datetime import datetime
import json 
import psutil
import subprocess
import re

from get_wifi import get_wifi, shell

clients = []


# sys.path.insert(0, './car/detector/yolov5')
cachedImage = np.array(Image.open('./car/detector/mygraph.png'))
def setImage(image):
    global cachedImage
    # filename = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    # cv2.imwrite("../../dump/{0}.jpg".format(filename), image)
    cachedImage = image

cachedPositions = '{}'
def setPositions(positions):
    global cachedPositions
    cachedPositions = positions

Cache = {}
def setCache(c):
    global Cache
    Cache = c

zed = {}
sl = {}
def setZed(c,l):
    global zed, sl
    zed = c
    sl = l

class SimpleChat(WebSocket):
    def handle(self):
        print("WebSocket Incomming Message: {0}".format(self.data))

    def connected(self):
        print(self.address, 'connected')
        for client in clients:
            client.send_message(self.address[0] + u' - connected')
        clients.append(self)

    def handle_close(self):
        clients.remove(self)
        print(self.address, 'closed')
        for client in clients:
            client.send_message(self.address[0] + u' - disconnected')

def sendWebsocketMessage(msg):
    for client in clients:
        client.send_message(str(msg))

class MyServer(http.server.SimpleHTTPRequestHandler):
    def get_file(self,file,t):
        with open("./dashboard/{}".format(file), 'r') as file:
            data = file.read()
            self.send_response(200)
            self.send_header('Content-type', t)
            self.end_headers()
            self.wfile.write(data.encode('utf-8'))
            return

    def get_css(self,file):
        return self.get_file(file,'text/css')

    def get_js(self,file):
        return self.get_file(file,'text/javascript')

    def get_html(self,file):
        return self.get_file(file,'text/html')

    def get_json(self,file):
        return self.get_file("json/{}".format(file),'application/json')

    def test(text):
        print(text)
    def log_message(self, format, *args):
        pass
    def do_POST(self):
        if self.path == '/zed':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
            post_data = self.rfile.read(content_length) # <--- Gets the data itself
            dic = json.loads(post_data)
            print(dic)
            if "BRIGHTNESS" in dic:
                zed.set_camera_settings(sl.VIDEO_SETTINGS.BRIGHTNESS,dic["BRIGHTNESS"])
            if "CONTRAST" in dic:
                zed.set_camera_settings(sl.VIDEO_SETTINGS.CONTRAST,dic["CONTRAST"])
            if "HUE" in dic:
                zed.set_camera_settings(sl.VIDEO_SETTINGS.HUE,dic["HUE"])
            if "SATURATION" in dic:
                zed.set_camera_settings(sl.VIDEO_SETTINGS.SATURATION,dic["SATURATION"])
            if "SHARPNESS" in dic:
                zed.set_camera_settings(sl.VIDEO_SETTINGS.SHARPNESS,dic["SHARPNESS"])
            if "GAMMA" in dic:
                zed.set_camera_settings(sl.VIDEO_SETTINGS.GAMMA,dic["GAMMA"])
            if "GAIN" in dic:
                zed.set_camera_settings(sl.VIDEO_SETTINGS.GAIN,dic["GAIN"])
            if "EXPOSURE" in dic:
                zed.set_camera_settings(sl.VIDEO_SETTINGS.EXPOSURE,dic["EXPOSURE"])
            if "AEC_AGC" in dic:
                zed.set_camera_settings(sl.VIDEO_SETTINGS.AEC_AGC,dic["AEC_AGC"])
            if "AEC_AGC_ROI" in dic:
                zed.set_camera_settings(sl.VIDEO_SETTINGS.AEC_AGC_ROI,dic["AEC_AGC_ROI"])
            if "WHITEBALANCE_TEMPERATURE" in dic:
                zed.set_camera_settings(sl.VIDEO_SETTINGS.WHITEBALANCE_TEMPERATURE,dic["WHITEBALANCE_TEMPERATURE"])
            if "WHITEBALANCE_AUTO" in dic:
                zed.set_camera_settings(sl.VIDEO_SETTINGS.WHITEBALANCE_AUTO,dic["WHITEBALANCE_AUTO"])
            if "LED_STATUS" in dic:
                zed.set_camera_settings(sl.VIDEO_SETTINGS.LED_STATUS,dic["LED_STATUS"])
            self.wfile.write(b"ok")
            return
    def do_GET(self):
        if self.path == '/':
            return self.get_html("index.html")
                
        if self.path.endswith('.css'):
            return self.get_css(self.path)
                
        if self.path.endswith('.js'):
            return self.get_js(self.path)
                
        if self.path.endswith('.html'):
            return self.get_html(self.path)
                
        if self.path.endswith('.json'):
            return self.get_json(self.path)
                
        if self.path == "/api/system":
            nic = "wlan0"
            hostName = ni.ifaddresses(nic)[ni.AF_INET][0]['addr']

            wifi = get_wifi()

            data = {
                "cpu": psutil.cpu_percent(),
                "ram": psutil.virtual_memory().percent,
                "ip": hostName,
                "wifi": wifi
            }
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            js = json.dumps(data)
            self.wfile.write(js.encode("utf-8"))
            return
        
        if self.path == '/power_mode':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            lines = shell('cat /etc/nvpmodel.conf  | grep "^< POWER_MODEL ID="')
            current_mode = shell('sudo nvpmodel -q')
            modes = []
            for line in lines:
                found = re.findall("< POWER_MODEL ID=(.*) NAME=(.*) >",line)
                if(len(found)>0 and len(found[0])>0):
                    modes.append({
                        "id": found[0][0],
                        "name": found[0][1],
                        "active": found[0][0] == current_mode[1]
                    })
                
            def test(x):
                return x["name"]
                
            modes.sort(key=test)
            self.wfile.write(json.dumps(modes).encode("utf-8"))
            return
        if self.path.startswith('/power_mode/'):
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            identity = re.findall("/power_mode/(.*)",self.path)
            wasFound = False
            if len(identity) > 0:
                lines = shell('cat /etc/nvpmodel.conf  | grep "^< POWER_MODEL ID="')
                current_mode = shell('sudo nvpmodel -q')
                modes = []
                for line in lines:
                    found = re.findall("< POWER_MODEL ID=(.*) NAME=(.*) >",line)
                    if(len(found)>0 and len(found[0])>0):
                        if found[0][0] == identity[0]:
                            lines = shell("sudo nvpmodel -m {}".format(identity[0]))
                            wasFound = True
                            break
            self.wfile.write(json.dumps({"success":wasFound}).encode("utf-8"))
            return
        if self.path == '/reset_cones':
            # global Cache
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            for color in list(Cache.keys()):
                if color!="self":
                    for item in list(Cache[color]["items"].keys()):
                        del Cache[color]["items"][item]
            print(Cache)
            self.wfile.write(b"done")
            return
        # if self.path.startswith('/image'):
        #     image = dataStore.get_image()
        #     if image is None:
        #         self.send_response(500)
        #         self.end_headers()
        #         return
        #     self.send_response(200)
        #     self.send_header('Content-type', 'image/jpeg')
        #     self.end_headers()

        #     # cachedImage[...,::-1].copy()

        #     # filename = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        #     # cv2.imwrite("../../dump/cached-{0}.jpg".format(filename), cachedImage)
        #     img = Image.fromarray(np.uint8(image[...,::-1].copy())).convert('RGB') #.astype(np.uint8)
        #     imgByteArr = io.BytesIO()
        #     img.save(imgByteArr, format="jpeg")
        #     imgByteArr = imgByteArr.getvalue()

        #     self.wfile.write(imgByteArr)
        #     return
        if self.path == '/zed':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            print("pre get")
            jsn = {
                "BRIGHTNESS": zed.get_camera_settings(sl.VIDEO_SETTINGS.BRIGHTNESS),
                "CONTRAST": zed.get_camera_settings(sl.VIDEO_SETTINGS.CONTRAST),
                "HUE": zed.get_camera_settings(sl.VIDEO_SETTINGS.HUE),
                "SATURATION": zed.get_camera_settings(sl.VIDEO_SETTINGS.SATURATION),
                "SHARPNESS": zed.get_camera_settings(sl.VIDEO_SETTINGS.SHARPNESS),
                "GAMMA": zed.get_camera_settings(sl.VIDEO_SETTINGS.GAMMA),
                "GAIN": zed.get_camera_settings(sl.VIDEO_SETTINGS.GAIN),
                "EXPOSURE": zed.get_camera_settings(sl.VIDEO_SETTINGS.EXPOSURE),
                "AEC_AGC": zed.get_camera_settings(sl.VIDEO_SETTINGS.AEC_AGC),
                "AEC_AGC_ROI": zed.get_camera_settings(sl.VIDEO_SETTINGS.AEC_AGC_ROI),
                "WHITEBALANCE_TEMPERATURE": zed.get_camera_settings(sl.VIDEO_SETTINGS.WHITEBALANCE_TEMPERATURE),
                "WHITEBALANCE_AUTO": zed.get_camera_settings(sl.VIDEO_SETTINGS.WHITEBALANCE_AUTO),
                "LED_STATUS": zed.get_camera_settings(sl.VIDEO_SETTINGS.LED_STATUS),
            }
            print("suf get")
            json_object = json.dumps(jsn, indent = 4) 
            print("dumped")
            self.wfile.write(json_object.encode('utf-8'))
            return
        if self.path == '/positions':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(cachedPositions.encode('utf-8'))
            return
        if self.path.startswith('/delete/'):
            # global Cache
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            lst = self.path.encode()[8:].decode('utf-8').split(":")
            # spt = lst[2:len(lst)-2].split(":")
            # print(lst)
            print(Cache)
            del Cache[lst[0]]["items"][int(lst[1])]
            # cachedPositions = json.dumps(Cache)
            print(Cache)
            self.wfile.write("Deleting item {0} from color {1}".format(lst[1],lst[0]).encode())
            return
        return http.server.SimpleHTTPRequestHandler.do_GET(self)

def startServers():
    nic = "wlan0"
    hostName = ni.ifaddresses(nic)[ni.AF_INET][0]['addr']
    serverPort = 8080
    print("Using {0}'s ip: {1}".format(nic,hostName))
    
    webServer = HTTPServer((hostName, serverPort), MyServer)
    print("Web Server started @ http://%s:%s" % (hostName, serverPort))

    server = WebSocketServer(hostName, serverPort+1, SimpleChat)
    print("WebSocket Server started @ http://%s:%s" % (hostName, serverPort+1))

    def start_web():
        webServer.serve_forever()

    def start_ws():
        server.serve_forever()

    try:
        webThread = threading.Thread(target=start_web)
        wsThread = threading.Thread(target=start_ws)
        webThread.start()
        wsThread.start()
    except KeyboardInterrupt:
        pass

    webThread.join()
    wsThread.join()
    webServer.server_close()
    print("Server stopped.")

def stopServer():
    webServer.terminate()
    server.terminate()