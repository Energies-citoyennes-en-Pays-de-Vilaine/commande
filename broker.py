import paho.mqtt.client as broker
import threading
import config
import logging
import time
import pgsql
import sys
import traceback
from devicemanager import DeviceManager

handler = None
stop = False

class MqttHandler ():
    def __init__ (self, cfg, mqtt):
        self.config = cfg
        self.mqtt = mqtt
        self.logger = logging.getLogger()
        self.value = -5
        self.devicemanager = DeviceManager.get_manager()
        
    def onConnect (self, client, userdata, flags, rc):
        self.logger.info ("MQTT broker connected")
        for topic in self.config.config['coordination']['permanent_topic']:
            client.subscribe(topic)
    
    def onDisconnect (self, client, userdata, rc):
        self.logger.info ("MQTT broker disconnected")
        self.__connect ()

    def onMessage (self, client, userdata, message):
        self.logger.info ("MQTT [{0}]-{1}".format (message.topic, message.payload.decode("utf-8")))
        details = message.topic.split ("/")
        if len(details) > 1:
            devicetype = details[0]
            device = details[1]
            self.devicemanager.incomingMessage(client, devicetype, device, message.topic, message.payload.decode("utf-8"))

       


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
    if handler != None:
        handler.loop ()

def threadtask ():
    setup ()
    while (not stop):
        try:
            loop ()
        except Exception as e:
            logging.getLogger().error("Exception : {0}".format (str(e)))
            tb = traceback.format_exc()
            logging.getLogger().error("Traceback : {0}".format (str(tb)))

def start ():
    thread = threading.Thread(target=threadtask)
    thread.start()
    return thread