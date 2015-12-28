#!/usr/env/bin python
import json
import requests
import threading
import time
from datetime import datetime
import serial

class DummyController:
    def __init__(self, uid="dummy"):
        self.uid = uid
    def parse(self):
        s = "{\"uid\":\"%s\",\"chksum\":0}" % (self.uid)
        d = json.loads(s)
        return d
    def checksum(self):
        return True
        
class Controller:
    def __init__(self, device='/dev/ttyACM0', baud=9600):
        self.port = serial.Serial(device, baud)
    def parse(self):
        if self.port.inWaiting() > 0:
            s = self.port.read()
        d = json.loads(s)
        return s
            
class Node:
    def __init__(self, config=None):
        self.config = config
        self.threads_active = True
        if self.config['CTRL_ON']:
            self.controller = serial.Serial(device, baud)
        else:
            self.controller = DummyController()
        threading.Thread(target=self.watchdog, args=(), kwargs={}).start()
            
    def watchdog(self):
        while self.threads_active == True:
            s = self.controller.parse()
    def ping(self, data):
        try:
            addr = self.config['SERVER_ADDR']
            print addr
            r = requests.post(addr, data={'@number': 12524, '@type': 'issue', '@action': 'show'})
            return None
        except Exception as e:
            print str(e)
            return (r.status_code, r.reason)
    def run(self):
        errors = None
        try:
            while errors is None:
                data = {}
                errors = self.ping(data)
        except KeyboardInterrupt:
            print "\nexiting..."
            self.threads_active = False
            exit(0)
    
if __name__ == '__main__':
    with open('default.cfg') as jsonfile:
        config = json.loads(jsonfile.read())
    node = Node(config=config)
    node.run()
