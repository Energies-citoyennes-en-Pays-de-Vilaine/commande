from device_doigt import DeviceDoigtRobot
from device_haspscreen import DeviceHaspScreen
import logging


class DeviceFactory ():
    def __init__(self):
        pass
    
    def CreateDevice (self, device_type):
        if device_type == 311:
            logging.getLogger().info ("Creating device {} {}".format(device_type, 'DeviceDoigtRobot'))
            return DeviceDoigtRobot ()
        else:
            return None
