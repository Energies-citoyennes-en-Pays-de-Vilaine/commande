import device
import logging
import json
import time
import datetime

class DeviceHaspScreen (device.Device):
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger()
        self.value = 0

    def incomingMessage (self, mqtt, devicetype, device, topic, payload):
        details = topic.split ("/")
         #  search for event
        if len(details) >=4:
            device = details[1]
            command = details[2]
            topic = details[3]
            if command == 'state':
                #event detected
                self.logger.info ("state change [{0}][{1}]-{2}".format (device, topic, payload))
                #give event to device manager

                mqtt.publish ('hasp/g002/command/jsonl', '{' +
                                '"page": 1,' +
                                '"id": 13,' +
                                '"val": "{0}",'.format (self.value) +
                                '"bg_color10": "#00FFFF"' +
                                '}')
                self.value += 1
                if self.value > 5:
                    self.value = -5
                
                if len(topic) >= 4:
                    if topic[0] == 'p' and topic[2] == 'b':
                        screen = int(topic[1])
                        button = int(topic[3:])
                        self.logger.info ("event {0} {1}".format (screen, button))

                        # get user
                        user = self.getUserFromEquipment (device)
                        self.logger.info ("user {0} found for device {1}:".format(user, device))

                        if screen == 1:
                            # select all
                            # get user equipement
                            devices = self.getEquipementFromUser (user)
                            self.logger.debug ("devices for user :{0} - {1}".format(user, devices))
                            
                        else:
                            self.logger.info ("search equipement_pilote_ou_mesure for user {0}.".format(user))    
                            actiondevice = self.getEquipementPiloteFromUserUsageType (user, screen, button)
                            print (actiondevice)
                            if len(actiondevice) == 0:
                                self.logger.warning ("no device found for screen {0} command {1}".format(device, topic) )
                            else:
                                equipement_pilote_ou_mesure_id = actiondevice[0][0]
                                equipement_domotique_type_id = actiondevice[0][0]
                                print (payload)
                                action = json.loads (payload)
                                print (action)
                                #self.execDeviceAction (actiondevice[0][0], actiondevice[0][2], payload)
                                if "event" in action:
                                    event = action["event"]
                                    if screen in  (2,3,4,5) and button == 3:
                                        if (event == "down" or event == "up") and "val" in action:
                                            query = "update {0} set equipement_pilote_ou_mesure_mode_id = {1} where id = {2} and etat_commande_id <> 60 and equipement_pilote_ou_mesure_mode_id in(20,30) ".format(
                                            self.config.config['coordination']['equipement_pilote_ou_mesure_table'],
                                            '20' if action["val"] == 0 else '30',   # 30 pilote / 20 manuel
                                            equipement_pilote_ou_mesure_id
                                            )   
                                            
                                            self.database.update_query (query, self.config.config['coordination']['database'])   
                                    
                                    if screen in (2,3,4) and button == 8:
                                        if event == "changed" and "val" in action and "text" in action:
                                            hour = int (action["text"][0:2])
                                            minute = 0
                                            
                                            prevts = self.GetEndTimestampFromEquipement (equipement_pilote_ou_mesure_id)
                                            if prevts != 0:
                                                current = datetime.datetime.fromtimestamp(prevts)
                                                minute = current.minute
                                                print ("time {0:02}:{1:02}".format (hour, minute))
                                            next_timestamp = self.prochain_horaire("{0:02}:{1:02}".format (hour, minute))
                                            self.SetEndTimestampFromEquipement(equipement_pilote_ou_mesure_id, next_timestamp)

                                    elif screen in (2,3,4) and button == 9:
                                        if event == "changed" and "val" in action and "text" in action:
                                            hour = 0
                                            minute = int (action["text"][0:2])
                                            
                                            prevts = self.GetEndTimestampFromEquipement (equipement_pilote_ou_mesure_id)
                                            if prevts != 0:
                                                current = datetime.datetime.fromtimestamp(prevts)
                                                hour = current.hour
                                                print ("time {0:02}:{1:02}".format (hour, minute))
                                            next_timestamp = self.prochain_horaire("{0:02}:{1:02}".format (hour, minute))
                                            self.SetEndTimestampFromEquipement(equipement_pilote_ou_mesure_id, next_timestamp)
                        
                        
    def outgoingMessage(self):
        pass
