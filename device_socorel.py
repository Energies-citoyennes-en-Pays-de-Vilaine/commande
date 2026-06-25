import device
import logging
import time
import elfeconstant
import typologie
import ems_broker
from devicecallback import DeviceCallback

class DeviceSocorel (device.Device):
    def __init__(self,ref = ""):
        super().__init__("{0}.{1}".format (ref, __name__))
        
        self.value = 0
        self.waitack = ""
        self.acknoledge = False
        self.output_number = 0
        self.output_status = "0"

    def incomingMessage (self, mqtt, devicetype, device, topic, payload):
        #self.logger.info ("Socorel incoming message :{0} payload {1}".format (topic, payload))
        self.mqtt = mqtt
        details = topic.split ("/")
        if len(details) >= 3:
            device = details[1]
            action = details[2]
            
            if action.lower() == "mode":
                self.logger.info ("Socorel incoming message  device:{0} action:{1} payload:{2}".format (device, action, payload))   
                if payload.lower() == "manuel":
                    self.logger.info ("Socorel passage en mode manuel device:{0}".format(device))
                    self.SetManualMode (device.lower())
                else:
                    self.logger.info ("Socorel passage en mode connecté device:{0}".format(device))
                    self.SetAutoMode (device.lower())

    def SetManualMode (self, material_id):
        user = self.getUserFromEquipment (material_id)
        self.logger.info ("Socorel user:{0}".format(user))
        if user == "":
            self.logger.warning("No user found for material_id:{0}".format(material_id))
            return
        devices = self.getDomotiqueDeviceListFromUser (user, elfeconstant.DOMO_TYPE_SOCOREL, material_id)
        
        for equipement in devices:
            equipement_pilote = equipement[1]
            pilote = self.GetEquipementPiloteFromId (equipement_pilote)
            if pilote != None:
                self.logger.info ("Socorel force disable on equipement_pilote:{0}".format (equipement_pilote))
                self.UpdateEquipementPiloteMode (elfeconstant.EQUIPEMENT_PILOTE_MODE_DISABLED, equipement_pilote)

    def SetAutoMode (self, material_id):
        user = self.getUserFromEquipment (material_id)
        self.logger.info ("Socorel user:{0}".format(user))
        if user == "":
            self.logger.warning("No user found for material_id:{0}".format(material_id))
            return
        devices = self.getDomotiqueDeviceListFromUser (user, elfeconstant.DOMO_TYPE_SOCOREL, material_id)
        
        for equipement in devices:
            equipement_pilote = equipement[1]
            
            pilote = self.GetEquipementPiloteFromId (equipement_pilote)
            if pilote != None:
                
                mode = self.GetEquipementPiloteMode(equipement_pilote)
                
                if mode == elfeconstant.EQUIPEMENT_PILOTE_MODE_DISABLED:
                    self.logger.info ("Socorel Reinitialisation en mode manuel equipement_pilote: {0}".format(equipement_pilote))
                    
                    #hack force equipement_pilote in manual mode before running typologie
                    self.UpdateEquipementPiloteMode (elfeconstant.EQUIPEMENT_PILOTE_MODE_MANUEL, equipement_pilote)
                    
                    # run typologie
                    typo = self.LoadTypologie (equipement_pilote)
                    if typo != None:                    
                        typo.InitMode (0)

    def LoadTypologie (self, machine_id):
        
         # get equipement pilote
        equipement_pilote = self.database.select_query(
            "SELECT id, equipement_pilote_specifique_id, typologie_installation_domotique_id, nom_humain, description, "
            "equipement_pilote_ou_mesure_type_id, equipement_pilote_ou_mesure_mode_id, etat_controle_id, etat_commande_id, "
            "ems_consigne_marche, timestamp_derniere_mise_en_marche, timestamp_derniere_programmation, utilisateur "
            " FROM {0} "
            "where id = {1};".
            format (
                self.config.config['coordination']['equipement_pilote_ou_mesure_table'],
                machine_id
            ), 
            self.config.config['coordination']['database'])  
        if len(equipement_pilote) == 0:
            self.logger.info ("Start typologie for machine_id :{0}".format(machine_id))
            return None
        #self.logger.info ("Start typologie for machine_id :{0}".format(machine_id))
        
        
        typo = typologie.Typologie (self.config, ems_broker.getBroker())
        typo.Setup (machine_id, equipement_pilote[0])
        return typo    

    def outgoingMessage(self, topic, payload):
        self.broker.SendMessage (topic, payload)

    def ems_callback_old (self, topic, payload):
        data = payload.decode('utf-8')
        
        if len(data) >= 8:
            if data[self.output_number] == self.output_status:
                self.logger.info ("device action ACK for {0} {1}".format (topic, payload))
                self.acknoledge = True
                return 0
        else:
            return 1
    def ems_callback (self, topic, payload):
        data = payload.decode('utf-8')
        
        if (data.find(self.waitack)) != -1:
            self.logger.debug ("equipement_domotique action ACK for {0} {1}".format (topic, payload))
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
            self.output_number = int(self.deviceinfo[3][-1]) -1
            self.output_status = "1"
            self.waitack = "1"
            self.outgoingMessage (self.deviceinfo[3], "1")

            begin = time.time ()
            while not self.acknoledge:
                time.sleep (0.5)
                if (time.time() - begin > 15):
                    break
            self.UpdateActivationTime (equipement_pilote_ou_mesure_id, time.time())        
            if not self.acknoledge:
                self.logger.warning ("timeout waiting for acknoledge equipement_domotique {0}".format (self.equipement_domotique_id))
                self.broker.UnRegisterCallback (self.deviceinfo[2])
                self.ProcessError (equipement_pilote_ou_mesure_id)
                result = -1
            else:
                self.logger.info ("Action acknoledged for equipement_domotique {0}".format (self.deviceinfo[1]))
                result = 1
        else:
            self.logger.debug ("{0} commande:{1}".format(type(self), commande))
            self.acknoledge = False
            callback = DeviceCallback (self)
            
            self.output_number = int(self.deviceinfo[3][-1]) -1
            self.output_status = "0"
            self.waitack = "0"
            self.broker.RegisterCallback (self.deviceinfo[2], callback)
            time.sleep (0.5)
            self.outgoingMessage (self.deviceinfo[3], "0")

            begin = time.time ()
            while not self.acknoledge:
                time.sleep (0.5)
                if (time.time() - begin > 30):
                    break

            if not self.acknoledge:
                self.logger.warning ("timeout waiting for acknoledge equipement_domotique {0}".format (self.equipement_domotique_id))
                self.broker.UnRegisterCallback (self.deviceinfo[2])
                self.ProcessError (equipement_pilote_ou_mesure_id)
                result = -1
            else:
                #self.UpdateActivationTime (equipement_pilote_ou_mesure_id, time.time())
                self.logger.info ("Action acknoledged for equipement_domotique {0}".format (self.deviceinfo[1]))
                result = 1
                
        return result