from device import Device

class DeviceCallback ():
    def __init__(self, device):
        self.device = device
    
    def exec (self, topic, payload):
        return self.device.ems_callback (topic, payload)
