import paho.mqtt.client as broker
import threading
import config
import logging
import time
import pgsql

stop = False
handler = None

CYCLE_TIME_SEC = 60 * 15

class EmsHandler ():
    def __init__(self, cfg):
        #init logger
        self.logger = logging.getLogger()
        # init last cycle
        self.lastcycle = time.time() - CYCLE_TIME_SEC + 15
        
        # backup config
        self.config = cfg
        
        #init database client
        self.database = pgsql.pgsql ()
        self.database.init (cfg.config['pgsql']['host'], 
                cfg.config['pgsql']['port'], 
                cfg.config['pgsql']['user'], 
                cfg.config['pgsql']['pass'], 
                cfg.config['pgsql']['database'])
        # cycle data backup
        self.cycledata = {}

        # start broker for temporary topic
        self.mqtt = broker.Client("ems_commande")

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
        if time.time() - self.lastcycle > CYCLE_TIME_SEC:
            # a new cycle start
            self.lastcycle = time.time()
            self.startCycle ()
            self.logger.info ("EMS Cycle duration {0}".format(time.time() - self.lastcycle))

            # check cyle time
            if time.time() - self.lastcycle > CYCLE_TIME_SEC:
                self.logger.warning ("EMS Cycle too long {0} s".format((time.time() - self.lastcycle) / 1000))
        
        else:
            time.sleep (0.5)
            

    def startCycle (self):
        self.logger.info ("EMS cycle started")
        # get data from database
        try:
            lastcycle = self.database.select_query ("select MAX(first_valid_timestamp) as lastts, machine_id "
                                                    "from {0} "
                                                    "group by machine_id order by machine_id;".
                                                    format (self.config.config['ems']['table']),
                                                    self.config.config['ems']['database']
                                                    )
            #print (lastcycle)
            for cycle in lastcycle:
                data = self.database.select_query ("select first_valid_timestamp, id, "
                                        "machine_id, result_type, machine_type, decisions_0, "
                                        "decisions_1, decisions_2, decisions_3, decisions_4, "
                                        "decisions_5, decisions_6, decisions_7, decisions_8, "
                                        "decisions_9, decisions_10, decisions_11, decisions_12, "
                                        "decisions_13, decisions_14, decisions_15, decisions_16, "
                                        "decisions_17, decisions_18, decisions_19, decisions_20, "
                                        "decisions_21, decisions_22, decisions_23, decisions_24, "
                                        "decisions_25, decisions_26, decisions_27, decisions_28, "
                                        "decisions_29, decisions_30, decisions_31, decisions_32, "
                                        "decisions_33, decisions_34, decisions_35, decisions_36, "
                                        "decisions_37, decisions_38, decisions_39, decisions_40, "
                                        "decisions_41, decisions_42, decisions_43, decisions_44, "
                                        "decisions_45, decisions_46, decisions_47, decisions_48, "
                                        "decisions_49, decisions_50, decisions_51, decisions_52, "
                                        "decisions_53, decisions_54, decisions_55, decisions_56, "
                                        "decisions_57, decisions_58, decisions_59, decisions_60, "
                                        "decisions_61, decisions_62, decisions_63, decisions_64, "
                                        "decisions_65, decisions_66, decisions_67, decisions_68, "
                                        "decisions_69, decisions_70, decisions_71, decisions_72, "
                                        "decisions_73, decisions_74, decisions_75, decisions_76, "
                                        "decisions_77, decisions_78, decisions_79, decisions_80, "
                                        "decisions_81, decisions_82, decisions_83, decisions_84, "
                                        "decisions_85, decisions_86, decisions_87, decisions_88, "
                                        "decisions_89, decisions_90, decisions_91, decisions_92, "
                                        "decisions_93, decisions_94, decisions_95"
                                        " FROM {0} where machine_id={1} and first_valid_timestamp ={2};".
                                        format (self.config.config['ems']['table'], cycle[1], cycle[0]),
                                        self.config.config['ems']['database']
                                        )
                # start cycle on device
                if len (data) > 0:
                    self.UpdateCycleInfo (data)
        except:            
               pass

        for cycle in self.cycledata.values():        
            self.startDeviceCycle (cycle)

        self.logger.info ("{0} devices processed in cycle".format(len(lastcycle)))

    def UpdateCycleInfo (self, cycledata):
        for data in cycledata:
            machine_id = data[2]
            self.cycledata[machine_id] = data
            
    def startDeviceCycle (self, cycledata):
        self.logger.debug ("device cycle data:".format(cycledata))  
        lastts = cycledata[0]
        lastid = cycledata[1]
        machine_id = cycledata[2]

        #get device info
        devicetype = self.database.select_query("SELECT {0}.id,equipement_domotique_type_id,nom FROM {0},{1} "
            "where {1}.id = {0}.equipement_domotique_type_id".
            format (
                self.config.config['coordination']['equipement_domotique_table'],
                self.config.config['coordination']['equipement_domotique_type_table']
            
            ), 
            self.config.config['coordination']['database'])
        
        self.logger.debug ("device type:".format(devicetype[0]))    

        #get device type info
        if len(devicetype) > 0:
            table = "{0}{1}".format(self.config.config['coordination']['equipement_domotique_table_root'], 
                                        devicetype[0][2])
            deviceinfo = self.database.select_query(
                    "SELECT id, equipement_domotique_id, topic_mqtt_controle_json, topic_mqtt_commande_text, topic_mqtt_lwt "
                    "FROM {0};".
                    format (table)
                )
            self.logger.debug ("device info:".format(deviceinfo))    
            
def setup ():
    global handler
    cfg = config.config.get_current_config()
    handler = EmsHandler (cfg)
    handler.setup ()

def loop ():
    if handler != None:
        handler.loop ()

def threadtask ():
    logging.getLogger().info("ems thread started")
    
    setup ()
    while (not stop):
        try:
            loop ()
        except Exception as e:
            logging.getLogger().error("Exception : {0}".format (str(e)))

def start ():
    thread = threading.Thread(target=threadtask)
    thread.start()
    return thread

def getDeviceManager ():
    return handler
