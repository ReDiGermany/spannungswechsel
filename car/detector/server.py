#!/usr/bin/python3.8
print("Welcome!")
from simple_websocket_server import WebSocketServer, WebSocket
from http.server import BaseHTTPRequestHandler, HTTPServer
import http.server
import time
import threading
import netifaces as ni
clients = []

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
    def do_GET(self):
        if self.path == '/':
            self.path = 'index.html'
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
