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
import tools.gui_tk as rhumGUI
import tools.lighting as rhumLighting
import tools.controller as rhumController

"""
Node Class
This class is responsible for acting as the HTTP interface between the remote manager (and/or local GUI) and controller(s)
"""
class Node:
    def __init__(self, config=None):
        self.config = config
        self.gui = None
        self.gui_exists = False
        self.threads_active = True
        self.remote_queue = [] # tasks set by the remote (start empty, e.g. local will override)
        self.controller = rhumController.Controller(rules=self.config['CTRL_CONF'])
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
            d['node_type'] = self.config['CTRL_CONF']
            print 'PUSH = ',
            print(json.dumps(d, indent=4, sort_keys=True))
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
            # Select GUI by controller type #!TODO set the node type      
            if self.config['CTRL_CONF'] == 'v1':
                self.gui = rhumGUI.GUI_v1() 
            if self.gui:
                self.gui.start()   
        time.sleep(1) #!TODO wait for controller to connect
        self.controller.set_params(self.gui.settings) #!TODO
            
        try:
            while ((len(self.remote_queue) < error_limit) or (error_limit is None)) and self.threads_active:
                time.sleep(1 / float(freq)) # slow down everyone, we're moving too fast
                
                # Handle GUI
                # Retrieve local changes to targets (overrides remote)
                if (self.gui is not None) and self.gui.active_changes:
                    print "------------------------------------"
                    gui_targets = self.gui.get_new_targets() #!TODO Resolve multiple sources for setting targets, GUI should override
                    self.controller.set_params(gui_targets)

                # Handle controller queue
                n = len(self.controller_queue)
                if n > 0:
                    print "------------------------------------"
                    try:
                        data = self.controller_queue.pop()
                        print 'CONTROLLER = ',
                        print json.dumps(data, indent=4, sort_keys=True)
                        for k in self.controller.rules.iterkeys():
                            pass #!TODO Maybe use the controller rules for the filering
                        data['targets']['lights_on'] = self.gui.settings['lights_on'] #!TODO Dangerous way to send lights values to remote
                        data['targets']['lights_off'] = self.gui.settings['lights_off']
                        data['targets']['photo1'] = self.gui.settings['photo1'] #!TODO Dangerous way to send lights values to remote
                        data['targets']['photo2'] = self.gui.settings['photo2']
                        while len(self.controller_queue) > queue_limit:
                            self.controller_queue.pop(0) # grab from out-queue
                        response = self.push_to_remote(data) # SEND TO REMOTE
                        if response is not None:
                            self.remote_queue.append(response)
                    except Exception as e:
                        print str(e)
                else:
                    d = {}
                    
                # Handled accrued responses/errors
                m = len(self.remote_queue)
                if m > 0:
                    for resp in self.remote_queue:
                        # ERROR CODES
                        if resp[0] == 200:
                            print 'RESPONSE = ',
                            print json.dumps(resp[1], indent=4, sort_keys=True)
                            if resp[1]['targets'] is not None:
                                self.controller.set_params(resp[1]['targets']) # send target values within response to controller
                                self.controller_queue = []
                                self.gui.settings.update(resp[1]['targets']) #!TODO Dangerous way to update GUI from remote
                            self.remote_queue.pop()
                        if resp[0] == 400:
                            print "WARN" + "400"     
                            self.remote_queue.pop() #!TODO bad connection!
                        if resp[0] == 500:
                            print "WARN" + "500"                            
                            self.remote_queue.pop() #!TODO server there, but uncooperative!
                        if resp[0] is None:
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
    
