from http.server import BaseHTTPRequestHandler, HTTPServer
from time import sleep
from urllib.parse import urlparse
import time
import base64
import json
import picamera
import os

hostName = "0.0.0.0"
hostPort = 8080

def deleteFile(fileName):
    # delete file if exists
    try:
        os.remove(fileName)
    except OSError:
        pass

class MyServer(BaseHTTPRequestHandler):
    key = ''

    def set_auth(self, username, password):
        self.key = base64.b64encode(
            bytes('%s:%s' % (username, password), 'utf-8')).decode('ascii')

    def get_auth_key(self):
        return self.key

    def do_AUTHHEAD(self):
        self.send_response(401)
        self.send_header(
            'WWW-Authenticate', 'Basic realm="Demo Realm"')
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    def do_GET(self):
        key = self.server.get_auth_key()

        ''' Present frontpage with user authentication. '''
        if self.headers.get('Authorization') == None:
            self.do_AUTHHEAD()

            response = {
                'success': False,
                'error': 'No auth header received'
            }

            self.wfile.write(bytes(json.dumps(response), 'utf-8'))
        elif self.headers.get('Authorization') == 'Basic ' + str(key):
            if self.path=="/":
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(bytes("<html><head><title>Title goes here.</title></head>", "utf-8"))
                self.wfile.write(bytes("<body><p>This is a test.</p>", "utf-8"))
                self.wfile.write(bytes("<p>You accessed path: %s</p>" % self.path, "utf-8"))
                self.wfile.write(bytes("</body></html>", "utf-8"))

            if self.path=="/video":
                path_to_video='/home/pi/video.h264'
                # delete file if exists
                deleteFile(path_to_video)
                camera.resolution = (640, 480)
                camera.start_recording(path_to_video)
                camera.wait_recording(5)
                camera.stop_recording()
                #Open the static file requested and send it
                f = open(path_to_video, 'rb')
                statinfo = os.stat(path_to_video)
                file_size = statinfo.st_size
                self.send_response(200)
                self.send_header('Content-type', 'video/h264')
                self.send_header("Content-length", file_size)
                self.end_headers(),
                self.wfile.write(f.read())
                f.close()
                deleteFile(path_to_video)

            if self.path=="/pic":
                path_to_image = '/home/pi/image.png'
                # delete file if exists
                deleteFile(path_to_image)
                camera.resolution = (1920, 1080)
                camera.capture(path_to_image)
                #Open the static file requested and send it
                f = open(path_to_image, 'rb')
                statinfo = os.stat(path_to_image)
                img_size = statinfo.st_size
                self.send_response(200)
                self.send_header('Content-type', 'image/png')
                self.send_header("Content-length", img_size)
                self.end_headers(),
                self.wfile.write(f.read())
                f.close()
                deleteFile(path_to_image)
        else:
            self.do_AUTHHEAD()

            response = {
                'success': False,
                'error': 'Invalid credentials'
            }

            self.wfile.write(bytes(json.dumps(response), 'utf-8'))

class CustomHTTPServer(HTTPServer):
    key = ''

    def set_auth(self, username, password):
        self.key = base64.b64encode(
            bytes('%s:%s' % (username, password), 'utf-8')).decode('ascii')

    def get_auth_key(self):
        return self.key

myServer = CustomHTTPServer((hostName, hostPort), MyServer)
print(time.asctime(), "Server Starts - %s:%s" % (hostName, hostPort))

camera = picamera.PiCamera()
# Turn the camera's LED off
camera.led = False

try:
    myServer.set_auth('admin', 'admin')
    myServer.serve_forever()
except KeyboardInterrupt:
    pass

myServer.server_close()
camera.close()
print(time.asctime(), "Server Stops - %s:%s" % (hostName, hostPort))