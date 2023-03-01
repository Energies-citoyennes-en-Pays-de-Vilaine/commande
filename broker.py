import paho.mqtt.client as broker
import threading
import config
import logging
import time

handler = None
stop = False

class MqttHandler ():
    def __init__ (self, cfg, mqtt):
        self.config = cfg
        self.mqtt = mqtt
        self.logger = logging.getLogger()
        self.value = -5
    def onConnect (self, client, userdata, flags, rc):
        self.logger.info ("MQTT broker connected")
        client.subscribe("hasp/#")
    
    def onDisconnect (self, client, userdata, rc):
        self.logger.info ("MQTT broker disconnected")
        self.__connect ()

    def onMessage (self, client, userdata, message):
        self.logger.info ("[{0}]-{1}".format (message.topic, message.payload.decode("utf-8")))
        details = message.topic.split ("/")
        
        #  search for event
        if len(details) >=3:
            device = details[1]
            topic = details[2]
            if topic == 'state':
                #event detected
                self.logger.info ("state change [{0}][{1}]-{2}".format (device, topic, message.payload.decode("utf-8")))
                #give event to device manager

                self.mqtt.publish ('hasp/g002/command/jsonl', '{' +
                                '"page": 1,' +
                                '"id": 13,' +
                                '"val": "{0}",'.format (self.value) +
                                '"bg_color10": "#00FFFF"' +
                                '}')
                self.value += 1
                if self.value > 5:
                    self.value = -5

    def __connect (self):
        for t in range (self.config.config['mqtt']['maxretry']):
            try:
                self.mqtt.connect(
                            host=self.config.config['mqtt']['host'], 
                            port=self.config.config['mqtt']['port'], 
                            keepalive=self.config.config['mqtt']['keepalive'])
                break                            
            except Exception as e:
                self.logger.error("MQTT connexion error :{}".format (e))
                time.sleep(self.config.config['mqtt']['retrydelaysec'])

    def setup (self):
        self.mqtt.username_pw_set(username=self.config.config['mqtt']['user'], 
                                    password=self.config.config['mqtt']['pass'])
        self.mqtt.on_connect = onconnect_handler
        self.mqtt.on_disconnect = ondisconnect_handler
        self.mqtt.on_message = onmessage_handler
        self.__connect()

    def loop (self):
        self.mqtt.loop (1)
        

def onconnect_handler (client, userdata, flags, rc):
    if not handler is None:
        handler.onConnect (client, userdata, flags, rc)

def onmessage_handler (client, userdata, message):
    if not handler is None:
        handler.onMessage (client, userdata, message)

def ondisconnect_handler(client, userdata, rc):
    if not handler is None:
        handler.onDisconnect (client, userdata, rc)

def setup ():
    global handler
    cfg = config.config.get_current_config()
    mqtt = broker.Client("commande")
    handler = MqttHandler (cfg, mqtt)
    handler.setup ()
    

def loop ():
    if (handler != None)
        handler.loop ()

def threadtask ():
    setup ()
    while (not stop):
        loop ()

def start ():
    thread = threading.Thread(target=threadtask)
    thread.start()
    return thread