
class Device ():
    def __init__(self):
        deviceroute = {
            'hasp': DeviceHaspScren ()
        }
    
    def incomingMessage (self, devicetype, device, topic, payload):
        pass
    
    def outgoingMessage(self):
        pass