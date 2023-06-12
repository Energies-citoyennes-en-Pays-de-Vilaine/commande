import device
import logging
import json
import time
import datetime
import ems_broker
import typologie
import elfeconstant
from device_haspscreen import DeviceHaspScreen

class DeviceVyria (device.Device):
    def __init__(self, ref=""):
        super().__init__("{0}.{1}".format (ref, __name__))
        
        self.value = 0
        self.haspdevice = None
        self.mqtt = None
        

    def SetMqtt (self, mqtt):
        self.mqtt = mqtt

    def LoadTypologie (self, machine_id, equipement_pilote):
        
        typo = typologie.Typologie (self.config, ems_broker.getBroker())
        typo.Setup (machine_id, equipement_pilote)
        return typo    

    def GetScreenIdMaterialFromUser (self, user):
        devices = self.database.select_query ("SELECT id_materiel "
                                                "FROM {0} "
                                                "WHERE utilisateur='{1}' and utilisateur_affecte = true and equipement_domotique_type_id={2};".
                                                    format (self.config.config['coordination']['equipement_domotique_table'],
                                                    user,
                                                    elfeconstant.EQUIPEMENT_PILOTE_TYPE_SCREEN
                                                    )
                                                )
        return devices

    def incomingMessage (self, mqtt, devicetype, device, topic, payload):
        self.mqtt = mqtt
        details = topic.split ("/")
         #  search for event
        if len(details) ==3:
            if details[1] == "update":
                self.logger.info ("viriya update {0}".format (details[2]))
                try:
                    equipement_pilote_ou_mesure_id = int(details[2])
                except:
                    self.logger.info ("viriya invalid equipement_pilote_ou_mesure_id {0}".format (details[2]))
                    return
                equipement_pilote = self.GetEquipementPiloteFromId(equipement_pilote_ou_mesure_id)
                print (equipement_pilote)
                if equipement_pilote == None:
                    self.logger.warning ("viriya error loading equipement_pilote_ou_mesure_id {0}".format (equipement_pilote_ou_mesure_id))
                    return

                typo = self.LoadTypologie (equipement_pilote_ou_mesure_id, equipement_pilote)
                if typo != None:
                    typo.InitMode (1 if equipement_pilote[6] == elfeconstant.EQUIPEMENT_PILOTE_MODE_PILOTE_NUM else 0)
                    
                    screenmaterial = self.GetScreenIdMaterialFromUser(equipement_pilote[12])
                    if screenmaterial != None:
                        for screen in screenmaterial:
                            hasp = DeviceHaspScreen (__name__)
                            hasp.SetMqtt (ems_broker.getBroker())
                            hasp.haspdevice = hasp.getEquipementFromMaterial_id(screen[0])
                            hasp.UpdateScreenPageButton (equipement_pilote_ou_mesure_id)
                else:
                    self.logger.warning ("viriya unknown equipement_pilote_ou_mesure_id {0}".format (equipement_pilote_ou_mesure_id))
            


                        
                        
    def outgoingMessage(self, topic, payload):
        if self.mqtt != None:
            self.logger.info ("send message to topic:{0} paylaod:{1}".format (topic, payload))
            self.mqtt.publish (topic, payload, qos=2)
