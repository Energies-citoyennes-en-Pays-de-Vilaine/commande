import paho.mqtt.client as broker
import threading
import datetime
import config
import logging
import time
import pgsql
import ems_broker
import typologie
from device_haspscreen import DeviceHaspScreen
import traceback
import elfeconstant

stop = False
handler = None

CYCLE_TIME_SEC = 60 * 15
CYCLE_TIME_DELAY = 60 * 15
DELAY_15MIN = 60 * 15

class EmsHandler ():
    def __init__(self, cfg):
        #init logger
        self.logger = logging.getLogger()
        # init last cycle
        self.lastcycle = time.time() - CYCLE_TIME_DELAY + 15
        self.nextcyle = time.time() + 15
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

        # equipement_domotique type
        self.continuous = self.config.config['coordination']['equipement_continu']

    def setup (self):
        pass
        
    def loop (self):
        if time.time() > self.nextcyle:
            # a new cycle start
            self.lastcycle = time.time()
            self.nextcyle = self.next_ems_cycle () + 5

            self.startCycle ()
            
            # check cycle time
            self.logger.info ("EMS Cycle duration {0}".format(time.time() - self.lastcycle))
            if time.time() - self.lastcycle > CYCLE_TIME_DELAY:
                self.logger.warning ("EMS Cycle too long {0} s".format(time.time() - self.lastcycle))
        
        else:
            time.sleep (0.5)
            
    def next_ems_cycle(self):
        now = int(time.time())
        quarter_hour = ((now // CYCLE_TIME_DELAY) + 1) * CYCLE_TIME_DELAY
        return quarter_hour

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
            if len(lastcycle) == 0:
                self.logger.warning ("No EMS result data")
                return
            
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
                                        format(self.config.config['ems']['table'], cycle[1], cycle[0]),
                                        self.config.config['ems']['database']
                                        )
                # start cycle on device
                if len (data) > 0:
                    self.UpdateCycleInfo (data)
        except:            
               pass

        for cycle in self.cycledata.values():        
            self.startTypologieCycle (cycle)

        self.logger.info ("{0} equipement_domotique processed in cycle".format(len(lastcycle)))

    def UpdateCycleInfo (self, cycledata):
        for data in cycledata:
            machine_id = data[2]
            self.cycledata[machine_id] = data
            
    def startTypologieCycle (self, cycledata):
        self.logger.debug ("equipement_pilote cycle data:{0}".format(cycledata))  
        lastts = cycledata[0]
        lastid = cycledata[1]
        machine_id = cycledata[2]

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
            self.logger.warning ("Unknown equipement_pilote with id:{0}".format(machine_id))        
            return
        elif len(equipement_pilote) > 1:
            self.logger.warning ("multiple equipement_pilote with id:{0} get only first".format(machine_id))
        
        

        equipement_pilote = equipement_pilote[0]

        if equipement_pilote[6] != elfeconstant.EQUIPEMENT_PILOTE_MODE_PILOTE_NUM:
            self.logger.info ("l'equipement domotique d'id {0} n'est pas en mode pilote".format (machine_id))
            return
        if equipement_pilote[9] != True:
            self.logger.info ("l'equipement domotique d'id {0} n'est pas asservi à l'EMS".format (machine_id))
            return
    
        # get equipement type ponctuel / continu
        continuous = 0
        if equipement_pilote[5] in self.continuous:
            continuous = 1

        # get cycle id
        if (True): #machine_id == 6:
            id = int((time.time () - lastts) /  CYCLE_TIME_SEC)
            id += 5 # offset in database cycledata

            self.logger.info ("Typologie cycle equipement_pilote {0} decision {1}, lastts {2} delta {3}".format (machine_id, id, lastts, time.time() - lastts))

            if id >= len(cycledata):
                self.logger.info ("Typologie equipement_pilote {0} no EMS info for 24H: {1}".format(machine_id, datetime.datetime.fromtimestamp(lastts, tz=None)))   
            elif continuous == 1 or cycledata[id] != 0:
                self.logger.info ("##################### Typologie start equipement_pilote id:{0} ######################".format(machine_id))   
                self.logger.debug ("#################### equipement_pilote id:{0} #########################".format(machine_id))   
                self.startTypologieFromEMS (machine_id, continuous, equipement_pilote, cycledata[id])   

            # update screen
            self.logger.info ("##################### Update screen for  machine_id:{0} ######################".format(machine_id))   
            screenmaterial = self.GetScreenIdMaterialFromUser(equipement_pilote[12])
            if screenmaterial != None:
                for screen in screenmaterial:
                    hasp = DeviceHaspScreen ()
                    hasp.SetMqtt (ems_broker.getBroker())
                    hasp.haspdevice = hasp.getEquipementFromMaterial_id(screen[0])
                    hasp.UpdateScreenPageButton (machine_id)

    def GetScreenIdMaterialFromUser (self, user):
        devices = self.database.select_query ("SELECT id_materiel "
                                                "FROM {0} "
                                                "WHERE utilisateur='{1}' and utilisateur_affecte = true and equipement_domotique_type_id={2};".
                                                    format (self.config.config['coordination']['equipement_domotique_table'],
                                                    user,
                                                    elfeconstant.EQUIPEMENT_PILOTE_TYPE_SCREEN
                                                    )
                                                )
        return devices

    def checkEmsResult (self, machine_id, cycledata):
        result = False
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
            self.logger.warning ("Unknown equipement_pilote with id:{0}".format(machine_id))        
            return False
        
        consigne_marche = equipement_pilote[0][9]
        ts_last_prog = equipement_pilote[0][11]
        if consigne_marche == True and ts_last_prog + DELAY_15MIN < time.time ():
            prog = 0
            for data in cycledata[5:]:
                prog += data
               


    def startTypologieFromEMS (self, machine_id, continuous, equipement_pilote, ems_consigne):
        #self.logger.info ("Start typologie for machine_id :{0}".format(machine_id))
        typo = typologie.Typologie (self.config, ems_broker.getBroker())
        typo.Setup (machine_id, equipement_pilote)
        typo.Start (continuous, ems_consigne)

    def startDeviceFromEms (self, machine_id, deviceinfo):
       pass

def setup ():
    global handler
    cfg = config.config.get_current_config()
    handler = EmsHandler (cfg)
    ems_broker.start ()
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
            tb = traceback.format_exc()
            logging.getLogger().error("Traceback : {0}".format (str(tb)))

def start ():
    thread = threading.Thread(target=threadtask)
    thread.start()
    return thread

def getDeviceManager ():
    return handler
