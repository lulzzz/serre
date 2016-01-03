#!/usr/env/bin python
import json
import requests
import threading
import time
from datetime import datetime
import serial
import sys
import random

class DummyController:
    def __init__(self, config='dummy.ctrl'):
        if type(config) == dict:
            self.conf = config
        else:
            with open(config) as jsonfile:
                self.conf = self.byteify(json.loads(jsonfile.read()))
        # .ctrl config needs these
        self.uid = self.conf['uid']
        self.check = self.conf['checksum']
        self.data = self.conf['data']
    def byteify(self, input):
        if isinstance(input, dict):
            return {self.byteify(key) : self.byteify(value) for key,value in input.iteritems()}
        elif isinstance(input, list):
            return [self.byteify(element) for element in input]
        elif isinstance(input, unicode):
            return input.encode('utf-8')
        else:
            return input
    def parse(self, interval=1.0, rand=False):
        time.sleep(interval)
        if rand:
            r = self.random(len(self.data))
            v = str(r)
        else:
            v = str(self.data).replace('\'', '\"')
        s = "{\"uid\":\"%s\",\"chksum\":%d,\"data\":%s}" % (self.uid, self.check, v)
        d = json.loads(s)
        if self.checksum(d):
            return d
    def random(self, n):
        r = [random.randint(0,i) for i in range(n)]
        return r
    def checksum(self, d, mod=256):
        b = d['chksum']
        chksum = 0
        s = str(d)
        s_clean = s.replace(' ', '')
        for i in s_clean:
            chksum += ord(i)
        # return chksum % mod
        return True
    def reset(self):
        pass
"""
Controller Class

SUPPORT:
JSON-only communication messages.

FUNCTIONS:
checksum()
parse()
reset()
"""
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
    def reset(self):
        pass
            
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
                d['time'] = datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")
                self.queue.append(d)
            except Exception as e:
                print str(e)
                self.threads_active == False
                self.errors.append(e)
    def ping(self, d):
        try:
            r = None
            addr = self.config['SERVER_ADDR']
            r = requests.post(addr, json=d)
            return (r.status_code, r.reason)
        except Exception as e:
            # print str(e)
            if r is not None:
                return (r.status_code, r.reason)
            else:
                return (400, 'Lost server')
    def run(self, queue_limit=16, error_limit=8):
        try:
            while (len(self.errors) < error_limit) and self.threads_active:
                n = len(self.queue)
                if n > 0:
                    try:
                        while len(self.queue) > queue_limit:
                            self.queue.pop(0) # grab from out-queue
                        d = self.queue.pop()
                        ce = self.ping(d)
                        if ce is not None:
                            self.errors.append(ce)
                    except Exception as e:
                        print str(e)
                else:
                    d = {}
                # Handle accrued errors
                m = len(self.errors)
                if m > 0:
                    for e in self.errors:
                        # ERROR CODES
                        if e[0] == 200:
                            self.errors.pop()
                        if e[0] == 400:
                            self.errors.pop() #!TODO bad connection!
                        if e[0] == 500:
                            self.errors.pop() # self.errors.pop() #!TODO server there, but uncooperative!
                        if e[0] is None:
                            self.errors.pop()
                        else:
                            pass #self.errors.pop() #!TODO Unknown errors 
                # Summary
                if d != {}:
                    s = "\rQueue: %d, Error: %s, Last: %s" % (n, str(ce), str(d))
                    sys.stdout.write(s)
                    sys.stdout.flush()
                # print "Queue: %d\tErrors: %d" % (n, m)
            else:
                print self.errors
        except KeyboardInterrupt:
            print "\nexiting..."
        except Exception as e:
            print str(e)
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
