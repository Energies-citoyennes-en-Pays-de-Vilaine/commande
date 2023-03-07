import device
import logging

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
                print ("command", command)
                if len(topic) >= 4:
                    if topic[0] == 'p' and topic[2] == 'b':
                        screen = int(topic[1])
                        button = int(topic[3:])
                        print ("event {0} {1}".format (screen, button))

                        # get user
                        user = self.getUserFromEquipment (device)
                        self.logger.debug ("get devices for user :{0}".format(user))

                        

                        if screen == 2:
                            # select all
                            # get user equipement
                            devices = self.getEquipementFromUser (user)
                            self.logger.debug ("devices for user :{0} - {1}".format(user, devices))
                            
                        else:    
                            actiondevice = self.getDeviceFromUserUsage (user, screen, button)
                            if len(actiondevice) == 0:
                                self.logger.info ("no device found for screen {0} command {1}".format(device, topic) )
                            else:
                                self.execDeviceAction (actiondevice[0], actiondevice[2], payload)

                        
    def outgoingMessage(self):
        pass
