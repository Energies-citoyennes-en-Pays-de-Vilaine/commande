from device_doigt import DeviceDoigtRobot
from device_haspscreen import DeviceHaspScreen
from device_tasmota import DeviceTasmota
from device_shellyplug import DeviceShellyPlug

import logging


class DeviceFactory ():
    def __init__(self):
        pass
    
    def CreateDevice (self, device_type):
        if device_type == 311:
            logging.getLogger().info ("Creating device {} {}".format(device_type, 'DeviceDoigtRobot'))
            return DeviceDoigtRobot ()
        elif device_type == 112:
            logging.getLogger().info ("Creating device {} {}".format(device_type, 'DeviceTasmota'))
            return DeviceTasmota ()
        elif device_type == 111:
            logging.getLogger().info ("Creating device {} {}".format(device_type, 'DeviceShellyPlug'))
            return DeviceShellyPlug ()
                    
        else:
            return None
