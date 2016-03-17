#!/usr/env/bin python
import json
import requests
import threading
import time
from datetime import datetime
import serial
import sys, os
import random
import Tkinter as tk
from itertools import cycle

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
    def __init__(self, rules='v1'):
        """
        rules : a .ctrl JSON-like file for I/O rules
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

    def byteify(self, input):
        if isinstance(input, dict):
            return {self.byteify(key) : self.byteify(value) for key,value in input.iteritems()}
        elif isinstance(input, list):
            return [self.byteify(element) for element in input]
        elif isinstance(input, unicode):
            return input.encode('utf-8')
        else:
            return input
    def parse(self, interval=1.0, chars=256):
        s = self.port.readline() #!TODO Need to handle very highspeed controllers, i.e. backlog
        try:
            d = json.loads(s) # parse as JSON
            if self.checksum(d): # Checksum of parsed dictionary
                return d
            else:
                return None
        except Exception as e:
            print str(e)
            return None
    def set_params(self, d):
        """ Set the target values of the controller """
        now = datetime.now()
        hours_since_midnight = (now - now.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds() / 3600.0
        d['time'] = hours_since_midnight
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
        if len(targets) == len(self.rules['data']):
            s = json.dumps(targets)
            s.replace(' ', '')
            self.port.write(s)
        else:
            print "Missing parameters when sending to controller!"
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
        return chksum % mod
    def reset(self):
        pass

"""
Tkinter GUI Class (local usage only)
"""
class GUI(threading.Thread):
    def __init__(self, settings='settings.json'):
        self.active_changes = False
        settings_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), settings)
        if os.path.exists(settings_path):
            with open(settings_path, 'r') as jsonfile:
                self.settings = json.loads(jsonfile.read())  
        else:
            self.settings =  {} # by default is empty until set
        self.active_changes = True
        threading.Thread.__init__(self)
    def run(self):
        self.root = tk.Tk()
        self.root.title("Hydroponics Controller")
        self.root.geometry("640x480")
        [self.root.rowconfigure(i,weight=1) for i in range(12)]
        [self.root.columnconfigure(i,weight=1) for i in range(3)]
        
        # Lights
        self.lights_on = tk.IntVar()
        self.lights_off = tk.IntVar()
        scale_lights_on = tk.Scale(self.root, from_=0.0, to=24.0, length=200, orient=tk.HORIZONTAL, variable = self.lights_on)
        scale_lights_on.grid(column=0, row=2, ipady=20)
        scale_lights_on.set(self.settings['lights_on'])
        scale_lights_off = tk.Scale(self.root, from_=0.0, to=24.0, length=200, orient=tk.HORIZONTAL, variable = self.lights_off)
        scale_lights_off.grid(column=0, row=3, ipady=20)
        scale_lights_off.set(self.settings['lights_off'])
        
        # Watering
        self.watering_time = tk.IntVar()
        self.scale_watering_time = tk.Scale(self.root, from_=0.0, to=60.0, length=200, orient=tk.HORIZONTAL, variable = self.watering_time)
        self.scale_watering_time.grid(column=1, row=2, ipady=20)
        self.scale_watering_time.set(self.settings['watering_time'])

        # Cycle Time
        self.cycle_time = tk.IntVar()
        self.scale_cycle_time = tk.Scale(self.root, from_=0.0, to=360.0, length=200, orient=tk.HORIZONTAL, variable = self.cycle_time)
        self.scale_cycle_time.grid(column=2, row=2, ipady=20)
        self.scale_cycle_time.set(self.settings['cycle_time'])

        # Set Button
        self.button_set = tk.Button(self.root, text="Set Configuration", command=self.set_config)
        self.button_set.grid(column=1, row=4)

        # Reset to saved values and start engine
        self.set_config()
        self.root.mainloop()
    def set_config(self, settings='settings.json'): # called from button_set object
        """
        Updates the dictionary object for settings provided by the GUI
        """        
        self.settings['lights_on'] = self.lights_on.get()
        self.settings['lights_off'] = self.lights_off.get()
        self.settings['watering_time'] = self.watering_time.get()
        self.settings['cycle_time'] = self.cycle_time.get()
        settings_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), settings)
        if os.path.exists(settings_path):
            with open(settings_path, 'w') as jsonfile:
                jsonfile.write(json.dumps(self.settings, indent=4))
        self.active_changes = True # (flag) changes are active!
    def get_new_targets(self):
        """
        Returns the dictionary object for settings provided by the GUI
        """
        self.active_changes = False # (flag) Once changes are retrieved, we assume that they will be sent to the controller
        return self.settings
    def update_config(self, settings):
        """
        Overrides the dictionary object for settings provided by the GUI
        """
        self.settings = settings
        self.scale_watering_time.set(settings['cycle_time'])
        self.scale_cycle_time.set(settings['cycle_time'])
        self.scale_lights_off.set(settings['lights_off'])
        self.scale_lights_on.set(settings['lights_on'])
    def close(self):
        self.root.destroy()
        
"""
Node Class
This class is responsible for acting as the HTTP interface between the remote manager (and/or local GUI) and controller(s)
"""
class Node:
    def __init__(self, config=None):
        self.config = config
        self.gui_exists = False
        self.threads_active = True
        self.remote_queue = [] # tasks set by the remote (start empty, e.g. local will override)
        self.controller = Controller(rules=self.config['CTRL_CONF'])
        self.controller_queue = [] # the outgoing queue (start empty)
        threading.Thread(target=self.watchdog, args=(), kwargs={}).start()
    def watchdog(self):
        while self.threads_active == True:
            try:
                d = self.controller.parse()
                now = datetime.now()
                datetimestamp = datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S") # grab the current time-stamp for the sample
                d['time'] = datetimestamp
                self.controller_queue.append(d) # add the sample to the outgoing queue to be handled by the node
            except Exception as e:
                print str(e)

    def push_to_remote(self, d):
        """
        Push current local settings to the remote manager
        """
        try:
            r = None
            d['uid'] = self.config['UID']
            addr = self.config['SERVER_ADDR']
            r = requests.post(addr, json=d)
            return (r.status_code, r.json())
        except Exception as e:
            if r is not None:
                return (r.status_code, r.reason)
            else:
                return (400, 'Lost server')
    def run(self, queue_limit=16, error_limit=None, gui=False, freq=10):
        """
        Run node as HTTP daemon
        Notes:
        * Node-App configuration is Push-Pull
        * For each iteration, the latest data gathered from the Controller is pushed from the Queue
        * Data is pushed to the App via HTTP Post to SERVER_ADDR
        * If the App has a task waiting, the task is returned as the response to the POST
        """
        if self.config['GUI']:
            self.gui = GUI()
            self.gui.start()
            self.gui_exists = True
            time.sleep(1) #!TODO wait for controller to connect
            self.controller.set_params(self.gui.settings) #!TODO
        else:
            self.gui_exists = False
            
        try:
            while ((len(self.remote_queue) < error_limit) or (error_limit is None)) and self.threads_active:
                time.sleep(1 / float(freq)) # slow down everyone, we're moving too fast
                
                # Handle GUI
                # Retrieve local changes to targets (overrides remote)
                if self.gui_exists and self.gui.active_changes:
                    gui_targets = self.gui.get_new_targets()
                    self.controller.set_params(gui_targets)

                # Handle controller queue
                n = len(self.controller_queue)
                if n > 0:
                    try:
                        data = self.controller_queue.pop()
                        if self.config['VERBOSE']: print data
                        while len(self.controller_queue) > queue_limit:
                            self.controller_queue.pop(0) # grab from out-queue
                        response = self.push_to_remote(data)
                        if response is not None:
                            self.remote_queue.append(response)
                    except Exception as e:
                        print str(e)
                else:
                    d = {}
                    
                # Handled accrued responses/errors
                m = len(self.remote_queue)
                if m > 0:
                    for e in self.remote_queue:
                        # ERROR CODES
                        if e[0] == 200:
                            self.remote_queue.pop() #!TODO Received response! possibly set new config values for controller!
                        if e[0] == 400:
                            print "WARN" + "400"     
                            self.remote_queue.pop() #!TODO bad connection!
                        if e[0] == 500:
                            print "WARN" + "500"                            
                            self.remote_queue.pop() #!TODO server there, but uncooperative!
                        if e[0] is None:
                            print "WARN" + "???"     
                            self.remote_queue.pop()
                        else:
                            pass #!TODO Unknown errors!
                # Summary
                if d != {}:
                    print "Queue: %d, Response: %s, Data: %s" % (n, str(ce), str(d['data']))
            else:
                print self.remote_queue #!TODO
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
    #node.run() # quickstart as daemon
    node.run(gui=True) # quickstart as GUI
    
