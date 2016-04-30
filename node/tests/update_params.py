timeout=5
port = serial.Serial(device, baud, timeout=timeout)
port.readline() #!TODO Need to handle very highspeed controllers, i.e. backlog
s = json.dumps(targets)
s.replace(' ', '') # remove whitespace for serial transmission
port.write(s)
return s

