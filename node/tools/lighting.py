import serial

class Lamp:
    def __init__(self, device="/dev/ttyUSB0", baud=115200):
        self.serial_port = serial.Serial(device, baud)
        self.manual_mode_command = "%d:%d s lamp.manual %d%%\r"
    def set_level(self, channel, percentage, group=1):
        """
        Manually set a particular channel of the lamp module to a percent level
        Channels
        """
        if percentage > 100:
            percentage = 100
        elif percentage < 0:
            percentage = 0
        if channel > 4 or channel < 1:
            raise Exception("Channel not recognized! Device only suppors channels 1-4")
        command = self.manual_mode_command % (group, channel, percentage)
        self.serial_port.write(command)
