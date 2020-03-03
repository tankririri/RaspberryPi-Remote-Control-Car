#!/usr/bin/python2
#coding=utf-8
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
import urllib
from abc import ABCMeta, abstractmethod
import RPi.GPIO as GPIO
import time
import configparser
 
 
class FourWheelDriveCar():
    # Define the number of all the GPIO that will used for the 4wd car
 
    def __init__(self):
        '''
        1. Read pin number from configure file
        2. Init all GPIO configureation
        '''
        config = configparser.ConfigParser()
        config.read("config.ini")
        self.LEFT_1 = config.getint("car", "LEFT_1")
        self.RIGHT_1 = config.getint("car", "RIGHT_1")
        self.LEFT_2 = config.getint("car", "LEFT_2")
        self.RIGHT_2 = config.getint("car", "RIGHT_2")
 
        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)
        GPIO.setup(self.LEFT_1, GPIO.OUT)
        GPIO.setup(self.RIGHT_1, GPIO.OUT)
        GPIO.setup(self.LEFT_2, GPIO.OUT)
        GPIO.setup(self.RIGHT_2, GPIO.OUT)
 
    def reset(self):
        # Rest all the GPIO as LOW
        GPIO.output(self.LEFT_1, GPIO.LOW)
        GPIO.output(self.RIGHT_1, GPIO.LOW)
        GPIO.output(self.LEFT_2, GPIO.LOW)
        GPIO.output(self.RIGHT_2, GPIO.LOW)
 
    def _RunCar__forward(self):
        self.reset()
        GPIO.output(self.LEFT_1, GPIO.HIGH)
        GPIO.output(self.RIGHT_1, GPIO.HIGH)
        GPIO.output(self.LEFT_2, GPIO.LOW)
        GPIO.output(self.RIGHT_2, GPIO.LOW)
 
    def _RunCar__backward(self):
        self.reset()
        GPIO.output(self.LEFT_1, GPIO.LOW)
        GPIO.output(self.RIGHT_1, GPIO.LOW)
        GPIO.output(self.LEFT_2, GPIO.HIGH)
        GPIO.output(self.RIGHT_2, GPIO.HIGH)
 
    def _RunCar__turnLeft(self):
        self.reset()
        GPIO.output(self.LEFT_1, GPIO.LOW)
        GPIO.output(self.RIGHT_1, GPIO.HIGH)
        GPIO.output(self.LEFT_2, GPIO.HIGH)
        GPIO.output(self.RIGHT_2, GPIO.LOW)
 
    def _RunCar__turnRight(self):
        self.reset()
        GPIO.output(self.LEFT_1, GPIO.HIGH)
        GPIO.output(self.RIGHT_1, GPIO.LOW)
        GPIO.output(self.LEFT_2, GPIO.LOW)
        GPIO.output(self.RIGHT_2, GPIO.HIGH)
 
    def _RunCar__stop(self):
        self.reset()

class DispatcherHandler(BaseHTTPRequestHandler):
        def do_GET(self):
                print 'client:', self.client_address, 'reuest path:', self.path, \
                                'command:', self.command
                #query = urllib.splitquery(self.path)
                query= self.path.split('?', 1)
                action = query[0]
                params = {}
                if len(query) == 2:
                        for key_value in query[1].split('&'):
                                kv = key_value.split('=')
                                if len(kv) == 2:
                                        params[kv[0]] = urllib.unquote(kv[1]).decode("utf-8", "ignore")
                runCar = RunCar()
                print(params)
                buf = {}
                if self.path.startswith("/car?"):
                        buf["return"] = runCar.action(params)
                else:
                        buf["return"] = -1
                self.protocal_version = "HTTP/1.1"
                self.send_response(200)
                self.send_header("Content-type", "application/json; charset=UTF-8")
                #self.send_header("Content-type", "test/html; charset=UTF-8")
                self.send_header("Pragma", "no-cache")
                self.send_header("Cache-Control", "no-cache")
                self.end_headers()
                self.wfile.write(buf)

        def do_POST(self):
                self.send_error(404)

class Job():
        __metaclass__ = ABCMeta
        @abstractmethod
        def action(self, params):
                pass
class RunCar(Job):
        car = FourWheelDriveCar()
        def action(self, params):
                print params
                act = int(params['a'])
                if act == 1:
                        self.car.__forward()
                        return 1
                if act == 2:
                        self.car.__backward()
                        return 1
                if act == 3:
                        self.car.__turnLeft()
                        return 1
                if act == 4:
                        self.car.__turnRight()
                        return 1
                if act == 0:
                        self.car.__stop()
                        return 1
                else:
                        return -1

if __name__ == "__main__":
        PORT_NUM = 8899
        serverAddress = ("", PORT_NUM)
        server = HTTPServer(serverAddress, DispatcherHandler)
        print 'Started httpserver on port: ', PORT_NUM
        try:
                server.serve_forever()
        except KeyboardInterrupt, e:
                pass
        finally:
                server.socket.close()
                print 'Exit...'