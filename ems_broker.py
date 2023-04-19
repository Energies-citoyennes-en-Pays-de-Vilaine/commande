import paho.mqtt.client as broker
import threading
import config
import logging
import time
import pgsql
import sys
import random

handler = None
stop = False

class EmsMqttHandler ():
    def __init__ (self, cfg, mqtt):
        self.config = cfg
        self.mqtt = mqtt
        self.logger = logging.getLogger()
        self.value = -5
        self.mutex = threading.Lock ()
        self.registered_topics = {}

    def onConnect (self, client, userdata, flags, rc):
        self.logger.info ("EMS MQTT broker connected")
        
    
    def onDisconnect (self, client, userdata, rc):
        self.logger.info ("EMS MQTT broker disconnected :{0}".format (rc))
        self.__connect ()

    def onMessage (self, client, userdata, message):
        self.logger.info ("ems-broker received [{0}]-{1}-{2}".format (message.topic, message.payload.decode("utf-8"), self.registered_topics))
        

        if self.mutex.acquire(True, timeout=2) :
            try:
                if message.topic in self.registered_topics:
                    if self.registered_topics[message.topic] != None:
                        if self.registered_topics[message.topic].exec (message.topic, message.payload) == 0:
                            self.mqtt.unsubscribe (message.topic)
                            self.registered_topics.pop(message.topic)
                            
                            self.logger.debug ("Unsubscribe {0} {1}".format (message.topic, str(self.registered_topics)))

            except Exception as e:
                raise  e
            finally:
                self.mutex.release()
        else:
            self.logger.warning ("Can't acquire mutex in ems_broker")
        

       


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

    def publish (self, topic, payload, qos=2):
        if self.mqtt != None:
            self.mqtt.publish (topic, payload, qos=qos)

    def setup (self):
        self.mqtt.username_pw_set(username=self.config.config['mqtt']['user'], 
                                    password=self.config.config['mqtt']['pass'])
        self.mqtt.on_connect = onconnect_handler
        self.mqtt.on_disconnect = ondisconnect_handler
        self.mqtt.on_message = onmessage_handler
        self.__connect()

    def loop (self):
        self.mqtt.loop (1)

    def RegisterCallback (self, topic, callback):
        if self.mutex.acquire(True, timeout=5) :
            try:
                self.registered_topics[topic] = callback
                self.mqtt.subscribe (topic, qos=2)

            except Exception as e:
                raise Exception('!!! Exception in mutex lock ems_broker.RegisterCallback()') from e
            finally:
                self.mutex.release()
        else:
            self.logger.warning ("Can't acquire mutex in ems_broker")

    def UnRegisterCallback (self, topic):
        if self.mutex.acquire(True, timeout=5) :
            try:
                if topic in self.registered_topics:
                    self.mqtt.unsubscribe (topic)
                    self.registered_topics.pop(topic)

            except Exception as e:
                raise Exception('!!! Exception in mutex lock ems_broker.RegisterCallback()') from e
            finally:
                self.mutex.release()
        else:
            self.logger.warning ("Can't acquire mutex in ems_broker")

    def SendMessage (self, topic, payload):
        if self.mutex.acquire(True, timeout=2) :
            try:
                self.logger.info ("send message to topic:{0} paylaod:{1}".format (topic, payload))
                self.mqtt.publish (topic, payload, qos=2)
            except Exception as e:
                raise Exception('!!! Exception in mutex lock ems_broker.SendMessage()') from e
            finally:
                self.mutex.release()
        else:
            self.logger.warning ("Can't acquire mutex in ems_broker")



        

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
    client_id = "ems_commande" + str(random.randint(1,65535))
    mqtt = broker.Client(client_id)
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
            tb = sys.exception().__traceback__
            logging.getLogger().error("Traceback : {0}".format (str(tb)))


def start ():
    thread = threading.Thread(target=threadtask)
    thread.start()
    return thread

def getBroker ():
    return handler



def register_and_publish (register_topic, publish_topic, payload):
    if handler != None:
        logging.getLogger().info("EMS MQTT Register topic: {0}".format (register_topic))
        logging.getLogger().info("EMS MQTT Send Command: {0}-{1}".format (publish_topic, payload))
        handler.mqtt.subscribe (register_topic)
        handler.mqtt.publish (publish_topic, payload)