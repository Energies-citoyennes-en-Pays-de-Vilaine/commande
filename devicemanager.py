from device_haspscreen import DeviceHaspScreen
from device_vyria import DeviceVyria
import logging
import logprefix

class DeviceManager ():
    __manager = None
    
    def __init__(self):
        self.route = {
            "hasp":DeviceHaspScreen (__name__),
            "viriya":DeviceVyria(__name__)
        }
        self.logger = logprefix.LogPrefix(__name__, logging.getLogger())
        
    
    def incomingMessage (self, mqtt, devicetype, device, topic, payload):
        
        if devicetype in self.route:
            self.route[devicetype].incomingMessage (mqtt, devicetype, device, topic, payload)
        else:
            self.logger.warning("unknow device type:{0}".format(devicetype))
    
    def outgoingMessage(self):
        pass

    def get_manager ():
        if DeviceManager.__manager is None:
            DeviceManager.__manager = DeviceManager ()
        return DeviceManager.__manager        