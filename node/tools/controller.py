import json
import requests
import threading
import time
from datetime import datetime
import serial
import sys, os
import random

class Controller:
    """
    Controller Class

    SUPPORT:
    JSON-only communication messages.

    FUNCTIONS:
    checksum()
    parse()
    reset()
    """
    def __init__(self, rules='v1'):
        """
        rules : The JSON-like .ctrl file for I/O rules
        """
        try:
            if type(rules) == dict:
                self.rules = rules
            else:
                cd = os.getcwd()
                configpath = os.path.join(cd, 'controllers', rules, rules + '.ctrl')
                with open(configpath) as jsonfile:
                    self.rules = self.byteify(json.loads(jsonfile.read()))
            
            # Check .ctrl integrity
            self.check = self.rules['checksum']
            self.data = self.rules['data']
            self.device = self.rules['device']
            self.baud = self.rules['baud']
        
        except Exception as e:
            raise e

        ## Attempt to grab port
        self.port = serial.Serial(self.device, self.baud)
        self.port_is_readable = True
        self.port_is_writable = True
    def byteify(self, input):
        if isinstance(input, dict):
            return {self.byteify(key) : self.byteify(value) for key,value in input.iteritems()}
        elif isinstance(input, list):
            return [self.byteify(element) for element in input]
        elif isinstance(input, unicode):
            return input.encode('utf-8')
        else:
            return input
    def parse(self, interval=1.0, chars=256, force_read=False): 
        try:
            s = self.port.readline() #!TODO Need to handle very highspeed controllers, i.e. backlog
            print s #!DEBUG
            d = json.loads(s) # parse as JSON
            self.port_is_readable = True
            if self.checksum(d): # Checksum of parsed dictionary
                return d
            else:
                return None
        except Exception as e:
            print str(e)
            return None
    def set_params(self, params):
        """
        Set the target values of the controller
        This checks the .ctrl rules file for each of the defined rulesets
        The named values in params are those which are passed either by the GUI or the remote host

        Currently supported rules
            * SETPOINT - Simply send the named value to the controller
            * IN_RANGE - Compare two values, if input value is within that range send 1, else send 0
        """
        now = datetime.now()
        hours_since_midnight = (now - now.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds() / 3600.0
        params['time'] = hours_since_midnight
        d = {k.encode('ascii'): v for (k, v) in params.items()}
        targets = dict()
        for k,r in self.rules['data'].iteritems():
            try:
                if r[0] == "SETPOINT": 
                    targets[k] = int(d[r[1]])
                if r[0] == "IN_RANGE": 
                    limit_max = d[r[3]]
                    limit_min = d[r[2]]
                    metric = d[r[1]]
                    if (metric < limit_max) and (metric > limit_min):
                        targets[k] = 1
                    else:
                        targets[k] = 0
            except Exception as e:
                print str(e)

        # Send parameters to controller
        s = json.dumps(targets)
        s.replace(' ', '') # remove whitespace for serial transmission
        self.port.write(s)
        return s
    def checksum(self, d, mod=256):
        b = d['chksum']
        chksum = 0
        s = str(d)
        s_clean = s.replace(' ', '')
        for i in s_clean:
            chksum += ord(i)
        return chksum % mod
    def reset(self):
        pass
