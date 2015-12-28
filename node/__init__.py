#!/usr/env/bin python
import json
import requests
import threading
import time
from datetime import datetime
import serial
    
class Node:
    def __init__(self, config=None, device='/dev/ttyACM0', baud=9600):
        self.config = config
        self.threads_active = True
        if self.config['CTRL_ON']:
            self.port = serial.Serial(device, baud)
            threading.Thread(target=self.watchdog, args=(), kwargs={}).start()
    def watchdog(self):
        while self.threads_active == True:
            if self.port.inWaiting() > 0:
                self.port.read()
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
