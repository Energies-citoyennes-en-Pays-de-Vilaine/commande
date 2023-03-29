import paho.mqtt.client as broker
import threading
import datetime
import config
import logging
import time
import pgsql
from device_factory import DeviceFactory

class TypologieScenario ():
    def __init__ (self, cfg, equipement_pilote_ou_mesure_id, equipement_domotiques, broker):
        self.equipement_domotique = equipement_domotiques            #equipement_domotique associe à la typologie
        self.equipement_domotique_usage = {}                        #equipement domotique associe au usage
        self.equipement_pilote_ou_mesure_id = equipement_pilote_ou_mesure_id
        self.logger = logging.getLogger()
        
        # backup config
        self.config = cfg
        
        #init database client
        self.database = pgsql.pgsql ()
        self.database.init (cfg.config['pgsql']['host'], 
                cfg.config['pgsql']['port'], 
                cfg.config['pgsql']['user'], 
                cfg.config['pgsql']['pass'], 
                cfg.config['pgsql']['database'])
        
        self.ems_broker = broker

    def GetDeviceInfoFromType (self, device_type_id, device_id):
        devicetype = self.database.select_query("SELECT id, nom "
            "from {0} "
            "where id= {1};".format (
            self.config.config['coordination']['equipement_domotique_type_table'],
            device_type_id))

        if len(devicetype) == 0:
            self.logger.warning("No equipement_domotique_type for id={0}".format(device_type_id))     
            return None

        table = "{0}{1}".format(self.config.config['coordination']['equipement_domotique_table_root'], 
                                            devicetype[0][1])
                
        deviceinfo = self.database.select_query(
                "SELECT id, equipement_domotique_id, topic_mqtt_controle_json, topic_mqtt_commande_text, topic_mqtt_lwt "
                "FROM {0} "
                "WHERE id={1}".
                format (table,
                device_id
                )
            )
        self.logger.debug ("device info:{0}".format(deviceinfo[0]))   

        info = self.database.select_query("SELECT id, equipement_domotique_id, topic_mqtt_controle_json, topic_mqtt_commande_text, topic_mqtt_lwt "
            "from {0} "
            "where equipement_domotique_id= '{1}';".format (
            table,
            device_id))
        
        if len(info) == 0:
            return None
        print (info[0])
        return info[0]

    def Setup (self):
        #dispatch devices in categorie
        self.logger.info ("Dispatch device in typologie")
        factory = DeviceFactory ()
        for device in self.equipement_domotique:
            print (device)
            
            equipement_domotique_id = device[0]
            equipement_domotique_specifique_id = device[8]
            equipement_domotique_type_id = device[2]
            equipement_domotique_usage_id = device[3]

            #get device info
            info = self.GetDeviceInfoFromType (equipement_domotique_type_id, equipement_domotique_specifique_id)
            if info == None:
                self.logger.warning ("Unknown device infos for equipement_domotique_specifique_id:{0} ({1})".
                    format (equipement_domotique_specifique_id, equipement_domotique_type_id))

            concrete = factory.CreateDevice(equipement_domotique_type_id)
            

            if concrete != None:
                concrete.SetEquipementDomotiqueId (equipement_domotique_id)
                concrete.SetEquipementPiloteOuMesureId (-1)
                concrete.SetDeviceInfo (info)
                concrete.SetBroker (self.ems_broker)
                self.equipement_domotique_usage[equipement_domotique_usage_id] = concrete

            else:
                self.logger.warning ("Unknown device type for equipement_domotique_usage_id:{0}".format (equipement_domotique_usage_id))


    def Run (self):
        self.logger.warning ("no scenario defined for {0}".format (type(self)))