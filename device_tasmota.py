import device
import logging
import time
import elfeconstant
from devicecallback import DeviceCallback

class DeviceTasmota (device.Device):
    def __init__(self, ref=""):
        super().__init__("{0}.{1}".format (ref, __name__))
        
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
    def ProcessError (self, equipement_pilote_ou_mesure_id):
        pass
        
    def Action (self, commande, equipement_pilote_ou_mesure_id):
        if commande == elfeconstant.DEVICE_ACTION_ON:
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
            
            self.UpdateActivationTime (equipement_pilote_ou_mesure_id, time.time())

            if not self.acknoledge:
                self.logger.warning ("timeout waiting for acknoledge equipement_domotique {0}".format (self.equipement_domotique_id))
                self.broker.UnRegisterCallback (self.deviceinfo[2])
                self.ProcessError (equipement_pilote_ou_mesure_id)
                result = -1
            else:
                self.logger.info ("Action acknoledged for device {0}".format (self.deviceinfo[1]))
                result = 1
        else:
            self.logger.debug ("{0} commande:{1}".format(type(self), commande))
            self.acknoledge = False
            callback = DeviceCallback (self)
            
            self.broker.RegisterCallback (self.deviceinfo[2], callback)
            time.sleep (0.5)
            self.outgoingMessage (self.deviceinfo[3], "OFF")

            begin = time.time ()
            while not self.acknoledge:
                time.sleep (0.5)
                if (time.time() - begin > 5):
                    break

            if not self.acknoledge:
                self.logger.warning ("timeout waiting for acknoledge equipement_domotique {0}".format (self.equipement_domotique_id))
                self.broker.UnRegisterCallback (self.deviceinfo[2])
                self.ProcessError (equipement_pilote_ou_mesure_id)
                result = -1
            else:
                #self.UpdateActivationTime (equipement_pilote_ou_mesure_id, time.time())
                self.logger.info ("Action acknoledged for device {0}".format (self.deviceinfo[1]))
                result = 1
                
        return result