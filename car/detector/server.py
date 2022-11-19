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

clients = []

cachedImage = np.array(Image.open('mygraph.png'))
def setImage(image):
    global cachedImage
    cachedImage = image

cachedPositions = '{}'
def setPositions(positions):
    global cachedPositions
    cachedPositions = positions

Cache = {}
def setCache(c):
    global Cache
    Cache = c

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
    def log_message(self, format, *args):
        pass
    def do_GET(self):
        if self.path == '/':
            self.path = 'index.html'
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
        if self.path.startswith('/image'):
            self.send_response(200)
            self.send_header('Content-type', 'image/jpeg')
            self.end_headers()

            # img_str = cv2.imencode('.jpg', cachedImage)[1].tostring()
            # nparr = np.fromstring(STRING_FROM_DATABASE, np.uint8)
            # img = cv2.imencode('.jpg',cachedImage).encode()
            img = Image.fromarray(np.uint8(cachedImage[...,::-1].copy())).convert('RGB') #.astype(np.uint8)
            imgByteArr = io.BytesIO()
            img.save(imgByteArr, format="jpeg")
            imgByteArr = imgByteArr.getvalue()

            self.wfile.write(imgByteArr)
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
