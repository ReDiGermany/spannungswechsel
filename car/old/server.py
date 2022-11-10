#!/usr/bin/python3.9
print("Welcome!")
from simple_websocket_server import WebSocketServer, WebSocket
from http.server import BaseHTTPRequestHandler, HTTPServer
import http.server
import time
import threading
print("Server libs loaded!")

from board import SCL_1, SDA_1
import busio
import time
from adafruit_pca9685 import PCA9685
from adafruit_servokit import ServoKit

from adafruit_motor import servo
print("Servo libs loaded!")

i2c = busio.I2C(SCL_1, SDA_1)
pca = PCA9685(i2c, address = 0x40)

Kit = ServoKit(channels=16,i2c=i2c)
print("Servo initiated!")

Kit.continuous_servo[0].throttle = 0.8
time.sleep(1/10)
Kit.continuous_servo[0].throttle = 0


class SimpleChat(WebSocket):
    def handle(self):
        test = self.data.split(":")
        print(test[0],"=",int(test[1]))
        if(test[0] == "angle"):
            print(90-int(test[1]))
            Kit.servo[1].angle = 90-int(test[1])
        if(test[0] == "speed"):
            print(int(test[1])/100)
            Kit.continuous_servo[0].throttle = int(test[1])/100
        # for client in clients:
        #     if client != self:
        #         client.send_message(self.address[0] + u' - ' + self.data)

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


clients = []


class MyServer(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.path = 'index.html'
        return http.server.SimpleHTTPRequestHandler.do_GET(self)

if __name__ == "__main__":
    # hostName = "192.168.0.19"
    # hostName = "192.168.171.134"
    hostName = "192.168.1.220"
    serverPort = 8080
    
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