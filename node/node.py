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
        """
        WatchDog Function
        Threaded function to listen for data from controller and parse it into Python readable info
        Associates each controller event with a datetime stamp
        Dies if threads_active becomes False
        """
        while self.threads_active == True:
            try:
                d = self.controller.parse() # Grab the latest response from the controller
                if d is None:
                    print("CHECKSUM: FAILED")
                else:
                    print("CHECKSUM: OK")
                now = datetime.now()
                datetimestamp = datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S") # grab the current time-stamp for the sample
                d['time'] = datetimestamp
                self.controller_queue.append(d) # add the sample to the outgoing queue to be handled by the node
            except Exception as e:
                print str(e)

    def push_to_remote(self, d):
        """
        Push current local settings to the remote manager
        Arguments:
            dict
        Returns:
            tuple of (code, msg)
        """
        try:
            r = None
            d['uid'] = self.config['UID']
            d['node_type'] = self.config['CTRL_CONF']
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
            # Select GUI by controller type
            if self.config['CTRL_CONF'] == 'v1':
                self.gui = rhumGUI.GUI_v1()
            if self.config['CTRL_CONF'] == 'bronfman':
                self.gui = rhumGUI.GUI_bronfman()
            else:
                print("GUI not found for \"%s\" configuration." % (self.config['CTRL_CONF']))
                self.threads_active = False
                exit(0)
            # If GUI started successfully, run as thread
            if self.gui:
                self.gui.start()   
        time.sleep(1)
        initial_params = self.controller.set_params(self.gui.settings) #!TODO
        gui_targets = None
        current_params = None
        try:
            while ((len(self.remote_queue) < error_limit) or (error_limit is None)) and self.threads_active:
                
                # Wait for next event
                time.sleep(1 / float(freq)) # slow down everyone, we're moving too fast

                # Handle GUI
                # Retrieve local changes to targets (overrides remote)
                if (self.gui is not None) and self.gui.active_changes:
                    gui_targets = self.gui.get_new_targets() #!TODO Resolve multiple sources for setting targets, GUI should override
                    current_params = self.controller.set_params(gui_targets)
                    print("GUI_TARGETS: %s" % gui_targets)
                    print("CURRENT_PARAMS: %s" % current_params)
                
                # Handle controller queue
                num_samples = len(self.controller_queue)
                if num_samples > 0:
                    print("LOCAL_QUEUE: %d" %  num_samples)
                    try:
                        sample = self.controller_queue.pop()
                        if (self.gui is not None): self.gui.update_values(sample['data'])
                        print("SAMPLE: %s" % str(sample))
                        while len(self.controller_queue) > queue_limit:
                            self.controller_queue.pop(0) # grab from out-queue
                        response = self.push_to_remote(sample) # SEND TO REMOTE
                        if response is not None:
                            self.remote_queue.append(response)
                    except Exception as e:
                        print str(e)

                # Handled accrued responses/errors
                num_responses = len(self.remote_queue)
                if num_responses > 0:
                    for resp in self.remote_queue:
                        print("REMOTE_QUEUE: %d" % num_responses)
                        print("RESPONSE: %s" % str(resp))
                        response_code = resp[0]
                        if response_code == 200:
                            target_values = resp[1]['targets']
                            if target_values is not None:
                                self.controller.set_params(target_values) # send target values within response to controller
                                self.controller_queue = []
                                self.gui.settings.update(target_values) #!TODO Dangerous way to update GUI from remote
                            self.remote_queue.pop()
                        if response_code == 400: 
                            self.remote_queue.pop() #!TODO bad connection!
                        if response_code == 500:
                            self.remote_queue.pop() #!TODO server there, but uncooperative!
                        if response_code is None:
                            self.remote_queue.pop()
                        else:
                            pass #!TODO Unknown errors!

        except KeyboardInterrupt:
            print "\nexiting..."
            self.threads_active = False
            exit(0)
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
    
