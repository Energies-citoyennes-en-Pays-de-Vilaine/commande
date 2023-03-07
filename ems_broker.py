import paho.mqtt.client as broker
import threading
import config
import logging
import time
import pgsql
from devicemanager import DeviceManager

handler = None
stop = False

class EmsMqttHandler ():
    def __init__ (self, cfg, mqtt):
        self.config = cfg
        self.mqtt = mqtt
        self.logger = logging.getLogger()
        self.value = -5
        self.devicemanager = DeviceManager.get_manager()
        
    def onConnect (self, client, userdata, flags, rc):
        self.logger.info ("EMS MQTT broker connected")
        
    
    def onDisconnect (self, client, userdata, rc):
        self.logger.info ("EMS MQTT broker disconnected")
        self.__connect ()

    def onMessage (self, client, userdata, message):
        self.logger.info ("ems-broker [{0}]-{1}".format (message.topic, message.payload.decode("utf-8")))
        details = message.topic.split ("/")
       

       


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
    mqtt = broker.Client("ems_commande")
    handler = EmsMqttHandler (cfg, mqtt)
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
            logging.getLogger().error("EMS MQTT Exception : {0}".format (str(e)))

def start ():
    thread = threading.Thread(target=threadtask)
    thread.start()
    return thread

def register_and_publish (register_topic, publish_topic, payload):
    if handler != None:
        logging.getLogger().info("EMS MQTT Register topic: {0}".format (register_topic))
        logging.getLogger().info("EMS MQTT Send Command: {0}-{1}".format (publish_topic, payload))
        handler.mqtt.register_topic (register_topic)
        handler.mqtt.publish (publish_topic, payload)