#!/usr/env/bin python
import json
import requests
import threading
import time
from datetime import datetime
import serial
import sys

class DummyController:
    def __init__(self, uid="dummy"):
        self.uid = uid
        self.sum = 0
        self.data = "{\"N\":0,\"P\":0,\"K\":0,\"Ca\":0}"
    def parse(self, interval=0.1):
        time.sleep(interval)
        s = "{\"uid\":\"%s\",\"chksum\":%d,\"data\":%s}" % (self.uid, self.sum, self.data)
        d = json.loads(s)
        if self.checksum(d):
            return d
    def checksum(self, d):
        return True
        
class Controller:
    def __init__(self, device='/dev/ttyACM0', baud=9600):
        self.port = serial.Serial(device, baud)
    def parse(self):
        if self.port.inWaiting() > 0:
            s = self.port.read()
        d = json.loads(s)
        return d
    def checksum(self, d, mod=256):
        chksum = 0
        s = str(d)
        s_clean = s.replace(' ', '')
        for i in s_clean:
            chksum += ord(i)
        return chksum % mod
            
class Node:
    def __init__(self, config=None):
        self.config = config
        self.threads_active = True
        self.errors = []
        if self.config['CTRL_ON']:
            self.controller = Controller(self.config['CTRL_DEVICE'], self.config['CTRL_BAUD'])
        else:
            self.controller = DummyController()
        self.queue = []
        threading.Thread(target=self.watchdog, args=(), kwargs={}).start()
    def watchdog(self):
        while self.threads_active == True:
            try:
                d = self.controller.parse()
                self.queue.append(d)
            except Exception as e:
                self.threads_active == False
                self.errors.append(e)
    def ping(self, d):
        try:
            r = None
            addr = self.config['SERVER_ADDR']
            r = requests.post(addr, json=d)
            return None
        except Exception as e:
            print 'An Exception occured in ping(): %s' % str(e)
            if r is not None:
                return (r.status_code, r.reason)
            else:
                return (400)
    def run(self):
        try:
            while (len(self.errors) == 0) and self.threads_active:
                time.sleep(0.01)
                n = len(self.queue)
                if n != 0:
                    d = self.queue.pop()
                    print n, d
                    e = self.ping(d)
                    if e is not None:
                        self.errors.append(e)
            else:
                print self.errors
        except KeyboardInterrupt:
            print "\nexiting..."
        self.threads_active = False
        exit(0)
    
if __name__ == '__main__':
    if len(sys.argv) > 1:
        configfile = sys.argv[1]
    else:
        configfile = 'default.cfg'
    with open(configfile) as jsonfile:
        config = json.loads(jsonfile.read())
    node = Node(config=config)
    node.run()
