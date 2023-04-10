import device
import logging
import time
import elfeconstant
from devicecallback import DeviceCallback

class DeviceShellyPlus1Pm (device.Device):
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger()
        self.value = 0
        self.acknoledge = False
        self.waitack = ""

    def incomingMessage (self, mqtt, devicetype, device, topic, payload):
        pass
                        
    def outgoingMessage(self, topic, payload):
        self.broker.SendMessage (topic, payload)

    def ems_callback (self, topic, payload):
        data = payload.decode('utf-8')
        
        if (data.find(self.waitack)) != -1:
            self.logger.info ("device action ACK for {0} {1}".format (topic, payload))
            self.acknoledge = True
            return 0
        else:
            return 1
    def ProcessError (self, equipement_pilote_ou_mesure_id):
        pass
        
    def Action (self, commande, equipement_pilote_ou_mesure_id):
        result = 0
        if commande == elfeconstant.DEVICE_ACTION_ON:
            commande = "on"
            self.logger.debug ("{0} commande:{1}".format(type(self), commande))
            self.acknoledge = False
            callback = DeviceCallback (self)
            
            self.waitack = commande
            self.broker.RegisterCallback (self.deviceinfo[2], callback)
            time.sleep (0.5)
            self.outgoingMessage (self.deviceinfo[3], commande)

            begin = time.time ()
            while not self.acknoledge:
                time.sleep (0.5)
                if (time.time() - begin > 5):
                    break

            if not self.acknoledge:
                self.logger.warning ("timeout waiting for acknoledge device {0}".format (self.deviceinfo[1]))
                self.broker.UnRegisterCallback (self.deviceinfo[2])
                #self.ProcessError (equipement_pilote_ou_mesure_id)
                result = -1
            else:
                result = 1    
                self.logger.info ("Action acknoledged for device {0}".format (self.deviceinfo[1]))

        elif commande == elfeconstant.DEVICE_ACTION_OFF:
            commande = "off"
            self.logger.debug ("{0} commande:{1}".format(type(self), commande))
            self.acknoledge = False
            callback = DeviceCallback (self)
            
            self.waitack = commande
            self.broker.RegisterCallback (self.deviceinfo[2], callback)
            time.sleep (0.5)
            self.outgoingMessage (self.deviceinfo[3], commande)

            begin = time.time ()
            while not self.acknoledge:
                time.sleep (0.5)
                if (time.time() - begin > 5):
                    break

            if not self.acknoledge:
                self.logger.warning ("timeout waiting for acknoledge device {0}".format (self.deviceinfo[1]))
                self.broker.UnRegisterCallback (self.deviceinfo[2])
                #self.ProcessError (equipement_pilote_ou_mesure_id)
            else:
                #update mode pilote / manuel
                query = "update {0} set equipement_pilote_ou_mesure_mode_id = {1} where id = {2} and etat_commande_id <> 60 and equipement_pilote_ou_mesure_mode_id in(20,30) ".format(
                                                self.config.config['coordination']['equipement_pilote_ou_mesure_table'],
                                                EQUIPEMENT_PILOTE_MODE_MANUEL,   # 30 pilote / 20 manuel
                                                equipement_pilote_ou_mesure_id
                                                )   
                #update timestamp derniere activation     
                
                if self.database.update_query (query, self.config.config['coordination']['database']) > 0:
                    query = "update {0} set timestamp_derniere_mise_en_marche = {1} where id = {2} and etat_commande_id <> 60 and equipement_pilote_ou_mesure_mode_id in(20,30) ".format(
                                                self.config.config['coordination']['equipement_pilote_ou_mesure_table'],
                                                time.time(),   
                                                equipement_pilote_ou_mesure_id
                                                )   
                    self.database.update_query (query, self.config.config['coordination']['database'])
                
                self.logger.info ("Action acknoledged for device {0}".format (self.deviceinfo[1]))