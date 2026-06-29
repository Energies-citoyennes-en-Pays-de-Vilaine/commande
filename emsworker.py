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
import elfeconstant
import logprefix

CYCLE_TIME_SEC = 60 * 15
CYCLE_TIME_DELAY = 60 * 15
DELAY_15MIN = 60 * 15



class EmsWorker ():
    """ 
    Thread Worker class for ems cycle execution of equipement_pilote 
    """
    def __init__ (self, cfg, broker, cycle):
        """
        Constructor

        Args:
            cfg : Configuration
            broker : ems_broker
            cycle : cycle data
        """
        
        
        # backup config
        self.config = cfg
        
        #init database client
        self.database = pgsql.pgsql (__name__)
        self.database.init (cfg.config['pgsql']['host'], 
                cfg.config['pgsql']['port'], 
                cfg.config['pgsql']['user'], 
                cfg.config['pgsql']['pass'], 
                cfg.config['pgsql']['database'])
        
        #init devices
        self.equipement_domotique = []
        
        self.machine_id = cycle[2]
        self.broker = broker
        #init logger
        self.logger = logprefix.LogPrefix("{0}.{1}".format(__name__, self.machine_id) , logging.getLogger())

        # equipement_domotique type
        self.continuous = self.config.config['coordination']['equipement_continu']

        self.cycle = cycle

    def startTypologieFromEMS (self, machine_id, continuous, equipement_pilote, ems_consigne):
        """Run typologie on equipement pilote

        Args:
            machine_id : equipement_pilote identifier
            continuous : continuous / normal
            equipement_pilote : equipement_pilote_data
            ems_consigne : ems consign (on /off)
        """
        #self.logger.info ("Start typologie for machine_id :{0}".format(machine_id))
        typo = typologie.Typologie (self.config, ems_broker.getBroker())
        typo.Setup (machine_id, equipement_pilote)
        typo.Start (continuous, ems_consigne)

    def startTypologieCycle (self):
        """
        Run an EMS cycle on equipement_pilote
        """
        cycledata = self.cycle
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
            self.logger.info ("l'equipement equipement_pilote_ou_mesure d'id {0} n'est pas en mode pilote".format (machine_id))
            return
                
        # get equipement type ponctuel / continu
        continuous = 0
        if equipement_pilote[5] in self.continuous:
            continuous = 1

        # get cycle id
        if (True): #machine_id == 6:
            id = int((time.time () - lastts) /  CYCLE_TIME_SEC)
            id += 5 # offset rows in database cycledata

            self.logger.info ("Typologie cycle equipement_pilote {0} decision {1}, lastts {2} delta {3}".format (machine_id, id, lastts, time.time() - lastts))

            if id >= len(cycledata):
                self.logger.info ("Typologie equipement_pilote {0} no EMS info for 24H: {1}".format(machine_id, datetime.datetime.fromtimestamp(lastts, tz=None)))   
            elif continuous == 1 or cycledata[id] != 0:
                self.logger.info ("##################### Typologie start equipement_pilote id:{0} ######################".format(machine_id))   
                self.logger.debug ("#################### equipement_pilote id:{0} #########################".format(machine_id))   
                self.startTypologieFromEMS (machine_id, continuous, equipement_pilote, cycledata[id])   
            elif equipement_pilote[2] == elfeconstant.TYPOLOGIE_PRISE: #then keep equipement_domotique in off state (so it resets auto-on timer) TODO generalize to all typologies
                self.logger.info ("##################### Typologie start equipement_pilote id:{0} ######################".format(machine_id))   
                self.logger.debug ("#################### equipement_pilote id:{0} #########################".format(machine_id))   
                self.startTypologieFromEMS (machine_id, continuous, equipement_pilote, cycledata[id])
                 

            # update screen
            self.logger.info ("##################### Update screen for  machine_id:{0} ######################".format(machine_id))   
            screenmaterial = self.GetScreenIdMaterialFromUser(equipement_pilote[12])
            if screenmaterial != None:
                for screen in screenmaterial:
                    hasp = DeviceHaspScreen (__name__)
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
