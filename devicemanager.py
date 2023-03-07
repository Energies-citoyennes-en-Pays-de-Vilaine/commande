from device_haspscreen import DeviceHaspScreen
import logging


class DeviceManager ():
    __manager = None
    
    def __init__(self):
        self.route = {
            "hasp":DeviceHaspScreen ()
        }
        
    
    def incomingMessage (self, mqtt, devicetype, device, topic, payload):
        if devicetype in self.route:
            self.route[devicetype].incomingMessage (mqtt, devicetype, device, topic, payload)
        else:
            logging.getLogger().warning("unknow device type:{0}".format(devicetype))
    
    def outgoingMessage(self):
        pass

    def get_manager ():
        if DeviceManager.__manager is None:
            DeviceManager.__manager = DeviceManager ()
        return DeviceManager.__manager        