"""
Tkinter GUI Class (local usage only)
"""
import threading
import os
import json

import Tkinter as tk
class GUI_v1(threading.Thread):
    def __init__(self, settings='../settings.json'):
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
        self.root.title("Hydroponics Controller (vers. 1)")
        self.root.geometry("640x480")
        [self.root.rowconfigure(i,weight=1) for i in range(12)]
        [self.root.columnconfigure(i,weight=1) for i in range(3)]
        
        # Lights
        self.lights_on = tk.IntVar()
        scale_lights_on = tk.Scale(self.root, from_=0.0, to=24.0, length=200, orient=tk.HORIZONTAL, variable = self.lights_on)
        scale_lights_on.grid(column=0, row=2, ipady=20)
        scale_lights_on.set(self.settings['lights_on'])
        self.lights_off = tk.IntVar()
        scale_lights_off = tk.Scale(self.root, from_=0.0, to=24.0, length=200, orient=tk.HORIZONTAL, variable = self.lights_off)
        scale_lights_off.grid(column=0, row=3, ipady=20)
        scale_lights_off.set(self.settings['lights_off'])
        self.photo1 = tk.IntVar()
        scale_photo1 = tk.Scale(self.root, from_=0, to=100, length=200, orient=tk.HORIZONTAL, variable = self.photo1)
        scale_photo1.grid(column=0, row=4, ipady=20)
        scale_photo1.set(self.settings['photo1'])
        self.photo2 = tk.IntVar()
        scale_photo2 = tk.Scale(self.root, from_=0, to=100, length=200, orient=tk.HORIZONTAL, variable = self.photo2)
        scale_photo2.grid(column=0, row=5, ipady=20)
        scale_photo2.set(self.settings['photo2'])
        
        # Watering
        self.watering = tk.IntVar()
        self.scale_watering = tk.Scale(self.root, from_=0.0, to=60.0, length=200, orient=tk.HORIZONTAL, variable = self.watering)
        self.scale_watering.grid(column=1, row=2, ipady=20)
        self.scale_watering.set(self.settings['watering'])
        self.smc1 = tk.IntVar()
        scale_smc1 = tk.Scale(self.root, from_=0, to=100, length=200, orient=tk.HORIZONTAL, variable = self.smc1)
        scale_smc1.grid(column=1, row=3, ipady=20)
        scale_smc1.set(self.settings['smc1'])
        self.smc2 = tk.IntVar()
        scale_smc2 = tk.Scale(self.root, from_=0, to=100, length=200, orient=tk.HORIZONTAL, variable = self.smc2)
        scale_smc2.grid(column=1, row=4, ipady=20)
        scale_smc2.set(self.settings['smc2'])
        self.smc3 = tk.IntVar()
        scale_smc3 = tk.Scale(self.root, from_=0, to=100, length=200, orient=tk.HORIZONTAL, variable = self.smc3)
        scale_smc3.grid(column=1, row=5, ipady=20)
        scale_smc3.set(self.settings['smc3'])
        self.smc4 = tk.IntVar()
        scale_smc4 = tk.Scale(self.root, from_=0, to=100, length=200, orient=tk.HORIZONTAL, variable = self.smc4)
        scale_smc4.grid(column=1, row=6, ipady=20)
        scale_smc4.set(self.settings['smc4'])

        # Cycle Time
        self.cycle = tk.IntVar()
        self.scale_cycle = tk.Scale(self.root, from_=0.0, to=360.0, length=200, orient=tk.HORIZONTAL, variable = self.cycle)
        self.scale_cycle.grid(column=2, row=2, ipady=20)
        self.scale_cycle.set(self.settings['cycle'])

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
        self.settings['photo1'] = self.photo1.get()
        self.settings['photo2'] = self.photo2.get()
        self.settings['smc1'] = self.smc1.get()
        self.settings['smc2'] = self.smc2.get()
        self.settings['smc3'] = self.smc3.get()
        self.settings['smc4'] = self.smc4.get()
        self.settings['watering'] = self.watering.get()
        self.settings['cycle'] = self.cycle.get()
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
        self.scale_watering.set(settings['watering'])
        self.scale_cycle.set(settings['cycle'])
        self.scale_lights_off.set(settings['lights_off'])
        self.scale_lights_on.set(settings['lights_on'])
        self.scale_photo1.set(settings['photo1'])
        self.scale_photo2.set(settings['photo2'])
        self.scale_smc1.set(settings['smc1'])
        self.scale_smc2.set(settings['smc2'])
        self.scale_smc3.set(settings['smc3'])
        self.scale_smc4.set(settings['smc4'])
    def close(self):
        self.root.destroy()
