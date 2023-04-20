import device
import logging
import json
import time
import datetime
import ems_broker
import typologie
import elfeconstant

class DeviceHaspScreen (device.Device):
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger()
        self.value = 0
        self.haspdevice = None
        self.mqtt = None
        self.offline_device = []

    def SetMqtt (self, mqtt):
        self.mqtt = mqtt

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

    def UpdateScreenPageButton (self, equipement_pilote_ou_mesure_id):
        color_pilote = "#00FF00"
        color_manual = "#FF0000"

        equipement_pilote = self.GetEquipementPiloteFromId (equipement_pilote_ou_mesure_id)
        if equipement_pilote == None:
            return
        if self.haspdevice == None:
            return
        
        # TODO: do something
        self.logger.info ("update screen for equipement_pilote: {0}".format (equipement_pilote_ou_mesure_id))
        hasp_equipement_domotique_specifique_id = self.haspdevice[8]
        hasp_equipement_domotique_type_id = self.haspdevice[2]
        
        if self.deviceinfo == None:
            self.deviceinfo = self.GetDeviceInfoFromType (hasp_equipement_domotique_type_id, hasp_equipement_domotique_specifique_id)
                
        equipement_type = equipement_pilote[5]
        equipement_mode = equipement_pilote[6]
        assoc = self.config.config['coordination']['screen_usage_assoc']
        messages = []
        for screen,types in assoc.items():
            if equipement_type in types:
                # update screen
                statusled = self.config.config['coordination']['screen_led_id']
                messages.append({"page":screen, "id":elfeconstant.SCREEN_OBJ_LED, "bg_color":color_pilote if equipement_mode == elfeconstant.EQUIPEMENT_PILOTE_MODE_PILOTE_NUM else color_manual})

                
                if screen in  ("2","3","4"):
                    tstamp = self.GetEndTimestampFromEquipement(equipement_pilote_ou_mesure_id)
                    horaire = datetime.datetime.fromtimestamp(tstamp)
                    messages.append({"page":screen, "id":elfeconstant.SCREEN_OBJ_TIME_HOUR, "val":horaire.hour })
                    messages.append({"page":screen, "id":elfeconstant.SCREEN_OBJ_TIME_MINUTE, "val":horaire.minute // 15 })
                    
                    tstamp = self.GetEndTimestampFromEquipement(equipement_pilote_ou_mesure_id)


                elif screen == "5":
                    tstamp = self.GetEndTimestampFromEquipementVoiture (equipement_pilote_ou_mesure_id)
                    messages.append({"page":screen, "id":elfeconstant.SCREEN_OBJ_VOITURE_TIME_HOUR, "val":horaire.hour })
                    messages.append({"page":screen, "id":elfeconstant.SCREEN_OBJ_VOITURE_TIME_MINUTE, "val":horaire.minute // 15 })
                    load = self.GetPendingLoadFromEquipement(equipement_pilote_ou_mesure_id)
                    messages.append({"page":screen, "id":elfeconstant.SCREEN_OBJ_VOITURE_LOAD, "val":horaire.minute // 15 })

                messages.append({"page":screen, "id":elfeconstant.SCREEN_OBJ_PILOTE_SWITCH, "val": 1 if equipement_mode == elfeconstant.EQUIPEMENT_PILOTE_MODE_PILOTE_NUM else 0})
                messages.append({"page":elfeconstant.SCREEN_PAGE_CONNEXION, "id":elfeconstant.SCREEN_OBJ_CONNEXION, "text": elfeconstant.SCREEN_TEXT_CONNEXION})
                messages.append({"page":elfeconstant.SCREEN_PAGE_CONNEXION, "id":elfeconstant.SCREEN_OBJ_CONNEXION, "text_color": "#008000"})

                #update status
                statusscreen = self.config.config['coordination']['screen_status_page']
                statusled = self.config.config['coordination']['screen_status_led'][screen]
                messages.append( {"page":str(statusscreen), "id":statusled, "bg_color":color_pilote if equipement_mode == 30 else color_manual})
                
                for msg in messages:
                    jscmd = json.dumps (msg)
                    self.outgoingMessage(self.deviceinfo[3], jscmd)
                break

    def incomingMessage (self, mqtt, devicetype, device, topic, payload):
        self.mqtt = mqtt
        details = topic.split ("/")
         #  search for event
        if len(details) ==3:
            if details[2] == "LWT" and payload == "online" and details[1] in self.offline_device:
                self.logger.debug ("refresh screen indicators")
                mqtt.publish ("Indicateurs/refresh", "1", qos=2)
                
                hasp = DeviceHaspScreen ()
                hasp.SetMqtt (ems_broker.getBroker())
                hasp.haspdevice = hasp.getEquipementDomotiqueFromIdMaterial(details[1])
                
                if hasp.haspdevice == None:
                    return
                
                equipement_pilote = self.GetEquipementPiloteFromUser (hasp.haspdevice[6])
                
                if equipement_pilote != None:
                    for pilote in equipement_pilote:
                        hasp.UpdateScreenPageButton (pilote[0])    

            elif details[2] == "LWT" and payload == "offline":
                self.offline_device.append (details[1])


        elif len(details) >=4:
            device = details[1]
            command = details[2]
            topic = details[3]
            if command == 'state':
                #event detected
                self.logger.debug ("state change [{0}][{1}]-{2}".format (device, topic, payload))
                #give event to device manager
                
                """
                mqtt.publish ('hasp/g002/command/jsonl', '{' +
                                '"page": 1,' +
                                '"id": 13,' +
                                '"val": "{0}",'.format (self.value) +
                                '"bg_color10": "#00FFFF"' +
                                '}')
                self.value += 1
                if self.value > 5:
                    self.value = -5
                """

                if len(topic) >= 4 and len(device) < 10:
                    if topic[0] == 'p' and topic[2] == 'b':
                        screen = int(topic[1])
                        button = int(topic[3:])
                        self.logger.info ("event screen {0} button {1} topic {2}".format (screen, button, topic))

                        # get user
                        #user = self.getUserFromEquipment (device)
                        self.haspdevice = self.getEquipementDomotiqueFromIdMaterial(device)
                        print ("haspdevice", self.haspdevice)
                        if self.haspdevice == None:
                            return
                        user = self.haspdevice[6]
                        if len(user) == 0:
                            return
                        
                        self.logger.info ("user {0} found for equipement_domotique {1}:".format(user, device))
                        if screen == 1:
                            # select all
                            # get user equipement
                            devices = self.getEquipementFromUser (user)
                            self.logger.info ("equipement_domotique for user :{0} - {1}".format(user, devices))
                            
                        else:
                            self.logger.info ("search equipement_pilote_ou_mesure for user {0}.".format(user))    
                            actiondevice = self.getEquipementPiloteFromUserUsageType (user, screen, button)
                            
                            if len(actiondevice) == 0:
                                self.logger.warning ("no device found for screen {0} command {1}".format(device, topic) )
                            else:
                                equipement_pilote_ou_mesure_id = actiondevice[0][0]
                                equipement_domotique_type_id = actiondevice[0][0]
                                
                                action = json.loads (payload)
                                
                                
                                if "event" in action and "val" in action:
                                    event = action["event"]
                                    val = action["val"]

                                    if screen in  (2,3,4,5,6,7) and button == 3 and event=="up": #mode pilote ou manuel
                                        # load a typologie to init state
                                        typo = self.LoadTypologie (equipement_pilote_ou_mesure_id)
                                        if typo != None:
                                            typo.InitMode (val)
                                            self.UpdateScreenPageButton (equipement_pilote_ou_mesure_id)
                                        # 
                                        """
                                        query = "update {0} set equipement_pilote_ou_mesure_mode_id = {1} where id = {2} and etat_commande_id <> 60 and equipement_pilote_ou_mesure_mode_id in(20,30) ".format(
                                            self.config.config['coordination']['equipement_pilote_ou_mesure_table'],
                                            '20' if action["val"] == 0 else '30',   # 30 pilote / 20 manuel
                                            equipement_pilote_ou_mesure_id
                                            )   
                                            
                                        self.database.update_query (query, self.config.config['coordination']['database'])   
                                        """
                                        self.logger.info ("Set equipement_pilote {0} in mode {1}".format(
                                                equipement_pilote_ou_mesure_id, "pilote" if action["val"] == 1 else "manuel" ) )

                                    if screen in (5,) and button == 5:   # voiture heure de fin
                                        if event == "changed" and "text" in action:
                                            hour = int (action["text"][0:2])
                                            minute = 0
                                            
                                            prevts = self.GetEndTimestampFromEquipementVoiture (equipement_pilote_ou_mesure_id)
                                            if prevts != 0:
                                                current = datetime.datetime.fromtimestamp(prevts)
                                                minute = (current.minute // (15 *60)) * (15*60)
                                                #print ("time {0:02}:{1:02}".format (hour, minute))
                                            next_timestamp = self.prochain_horaire("{0:02}:{1:02}".format (hour, minute))
                                            self.SetEndTimestampFromEquipementVoiture(equipement_pilote_ou_mesure_id, next_timestamp)
                                    
                                    elif screen in (5,) and button == 6:   # voiture minute de fin
                                         if event == "changed" and "text" in action:
                                            hour = 0
                                            minute = int (action["text"][0:2])
                                            
                                            prevts = self.GetEndTimestampFromEquipementVoiture (equipement_pilote_ou_mesure_id)
                                            if prevts != 0:
                                                current = datetime.datetime.fromtimestamp(prevts)
                                                hour = current.hour
                                                #print ("time {0:02}:{1:02}".format (hour, minute))
                                            next_timestamp = self.prochain_horaire("{0:02}:{1:02}".format (hour, minute))
                                            self.SetEndTimestampFromEquipementVoiture(equipement_pilote_ou_mesure_id, next_timestamp)
                                    
                                    elif screen in (5,) and button == 8:   # voiture charge restante
                                        if event == "changed" and "text" in action:
                                            percent = int (action["text"][0:2])
                                            self.SetPendingLoadFromEquipement (equipement_pilote_ou_mesure_id, percent)
                                            
                                        
                                    elif screen in (2,3,4) and button == 8: # electromenager heure de fin
                                        if event == "changed" and "text" in action:
                                            hour = int (action["text"][0:2])
                                            minute = 0
                                            
                                            prevts = self.GetEndTimestampFromEquipement (equipement_pilote_ou_mesure_id)
                                            if prevts != 0:
                                                current = datetime.datetime.fromtimestamp(prevts)
                                                minute = (current.minute // (15 *60)) * (15*60)
                                                #print ("time {0:02}:{1:02}".format (hour, minute))
                                            next_timestamp = self.prochain_horaire("{0:02}:{1:02}".format (hour, minute))
                                            self.SetEndTimestampFromEquipement(equipement_pilote_ou_mesure_id, next_timestamp)

                                    elif screen in (2,3,4) and button == 9: # electromenager minute de fin
                                        if event == "changed" and "text" in action:
                                            hour = 0
                                            minute = int (action["text"][0:2])
                                            
                                            prevts = self.GetEndTimestampFromEquipement (equipement_pilote_ou_mesure_id)
                                            if prevts != 0:
                                                current = datetime.datetime.fromtimestamp(prevts)
                                                hour = current.hour
                                                #print ("time {0:02}:{1:02}".format (hour, minute))
                                            next_timestamp = self.prochain_horaire("{0:02}:{1:02}".format (hour, minute))
                                            self.SetEndTimestampFromEquipement(equipement_pilote_ou_mesure_id, next_timestamp)
                        
                        
    def outgoingMessage(self, topic, payload):
        if self.mqtt != None:
            self.logger.info ("send message to topic:{0} paylaod:{1}".format (topic, payload))
            self.mqtt.publish (topic, payload, qos=2)
