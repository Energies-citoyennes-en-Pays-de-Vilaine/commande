from device_doigt import DeviceDoigtRobot
from device_tasmota import DeviceTasmota
from device_shellyplug import DeviceShellyPlug
from device_shellyplus1pm import DeviceShellyPlus1Pm
from device_socorel import DeviceSocorel
import elfeconstant

import logging


class DeviceFactory ():
    def __init__(self):
        pass
    
    def CreateDevice (self, device_type, ref):
        if device_type == elfeconstant.DOMO_TYPE_SOCOREL:
            logging.getLogger().info ("[{}.{}] Creating device {} {}".format(ref, __name__, device_type, 'DeviceSocorel'))
            return DeviceSocorel (ref)
        if device_type == elfeconstant.DOMO_TYPE_SHELLYPLUS:
            logging.getLogger().info ("[{}.{}] Creating device {} {}".format(ref, __name__, device_type, 'DeviceShellyPlus1Pm'))
            return DeviceShellyPlus1Pm (ref)
        elif device_type == elfeconstant.DOMO_TYPE_DOIGT:
            logging.getLogger().info ("[{}.{}] Creating device {} {}".format(ref, __name__, device_type, 'DeviceDoigtRobot'))
            return DeviceDoigtRobot (ref)
        elif device_type == elfeconstant.DOMO_TYPE_TASMOTA:
            logging.getLogger().info ("[{}.{}] Creating device {} {}".format(ref, __name__, device_type, 'DeviceTasmota'))
            return DeviceTasmota (ref)
        elif device_type == elfeconstant.DOMO_TYPE_SHELLYPLUG:
            logging.getLogger().info ("[{}.{}] Creating device {} {}".format(ref, __name__, device_type, 'DeviceShellyPlug'))
            return DeviceShellyPlug (ref)

        else:
            return None
