import device
import logging
import time
from devicecallback import DeviceCallback

class DeviceDoigtRobot (device.Device):
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger()
        self.value = 0
        self.acknoledge = False

    def incomingMessage (self, mqtt, devicetype, device, topic, payload):
        pass
                        
    def outgoingMessage(self, topic, payload):
        self.broker.SendMessage (topic, payload)

    def ems_callback (self, topic, payload):
        data = payload.decode('utf-8')
        
        if (data.find("success")) != -1:
            self.logger.info ("device action ACK for {0} {1}".format (topic, payload))
            self.acknoledge = True
            return 0
        else:
            return 1
    def ProcessError (self):
        pass
        
    def Action (self, commande):
        self.logger.debug ("{0} commande:{1}".format(type(self), commande))
        self.acknoledge = False
        callback = DeviceCallback (self)
        self.broker.RegisterCallback (self.deviceinfo[2], callback)
        time.sleep (0.5)
        self.outgoingMessage (self.deviceinfo[3], "ON")

        begin = time.time ()
        while not self.acknoledge:
            time.sleep (0.5)
            if (time.time() - begin > 5):
                break

        if not self.acknoledge:
            self.logger.warning ("timeout waiting for acknoledge device {0}".format (self.deviceinfo[1]))
            self.broker.UnRegisterCallback (self.deviceinfo[2])
            self.ProcessError ()
        else:
            self.logger.info ("Action acknoledged for device {0}".format (self.deviceinfo[1]))