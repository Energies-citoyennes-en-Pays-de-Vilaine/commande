import paho.mqtt.client as broker
import threading
import datetime
import config
import logging
import time
import pgsql
import typologiescenario_factory
import elfeconstant


class Typologie ():
    def __init__ (self, cfg, broker):
        #init logger
        self.logger = logging.getLogger()
        
        # backup config
        self.config = cfg
        
        #init database client
        self.database = pgsql.pgsql ()
        self.database.init (cfg.config['pgsql']['host'], 
                cfg.config['pgsql']['port'], 
                cfg.config['pgsql']['user'], 
                cfg.config['pgsql']['pass'], 
                cfg.config['pgsql']['database'])
        
        #init devices
        self.equipement_domotique = []
        
        self.machine_id = -1
        self.broker = broker

    #initialize typologie from typologie_id (ie machine_id in ems result)
    def Setup (self, machine_id, equipement_pilote):
        """
        Initialise une typologie a partir d'un equipement domotique

        arguments:
        machine_id          id de l'equipement domotique (machine_id dans la sortie ems)
        equipement_pilote   enregistrement de l'equipement_pilote en base de données
        """
               
        self.machine_id = machine_id    
        self.equipement_pilote = equipement_pilote
        self.typologie_type_id = self.equipement_pilote[2]
        self.equipement_pilote_id = self.equipement_pilote[0]

        self.logger.debug ("Start typologie type_id:{0}".format(self.typologie_type_id))    

        # get typologie
        typologie = self.database.select_query("SELECT id, nom, nom_humain, description "
            " FROM {0} "
            "where id = {1};".
            format (
                self.config.config['coordination']['equipement_pilote_typologie_installation_domotique'],
                self.typologie_type_id
        ), 
        self.config.config['coordination']['database'])
        
        if len(typologie) == 0:
            self.logger.warning ("Unknown typologie with id:{0}".format(self.typologie_type_id))        
            return -1
        elif len(typologie) > 1:
            self.logger.warning ("Multiple typologie with id:{0}".format(self.typologie_type_id))        

        self.typologie = typologie[0]
        # load devices
        equipement_domotique = self.database.select_query("SELECT id, equipement_pilote_ou_mesure_id, equipement_domotique_type_id, "
            "equipement_domotique_usage_id, id_materiel, marque, utilisateur, utilisateur_affecte, "
            "equipement_domotique_specifique_id "

            " FROM {0} "
            "where equipement_pilote_ou_mesure_id = {1} AND "
            "utilisateur = '{2}';".
            format (
                self.config.config['coordination']['equipement_domotique_table'],
                self.equipement_pilote_id,
                self.equipement_pilote[12]
        ), 
        self.config.config['coordination']['database'])
             
        self.equipement_domotique = equipement_domotique
        
        #create a typologie scenario from id
        factory = typologiescenario_factory.TypologieScenarioFactory ()
        self.typo_scenario = factory.CreateScenario (self.typologie_type_id, self.config, 
            self.machine_id ,self.equipement_domotique, self.broker)
        if self.typo_scenario == None:
            return -1
        
        return len(equipement_domotique)

    
    def Start (self, continuous, ems_consign):
        """
            Demarre une typologie sur instruction de l'EMS            
        
        arguments:
        continuous 0 si mode normal / 1 si mode continue
        ems_consign 0 si equipement OFF / 1 si equipement ON
        """
        if self.typo_scenario == None:
            self.logger.warning ("unknown typologie")        
            return -1           
        
        if len(self.equipement_domotique) == 0:
            self.logger.warning ("No devices in typologie. Can't start")        
            return -1
        
        if self.equipement_pilote[6] != elfeconstant.EQUIPEMENT_PILOTE_MODE_PILOTE_NUM:
            self.logger.info ("equipement_pilote :{0} n'est pas en mode pilote".format(self.equipement_pilote_id))    
            return -1
        
        if self.typo_scenario.Setup () == -1:
            self.logger.info ("equipement_pilote :{0} erreur à l'initialisation".format(self.equipement_pilote_id))    
            return -1

        self.typo_scenario.Run (continuous, ems_consign)
        return 1

    def InitMode (self, val):
        """
            Demarre une typologie sur passage manuel / pilote            

            arguments:
            val     0 mode manuel / 1 mode pilote
        """                     
        if self.typo_scenario == None:
            self.logger.warning ("unknown typologie")        
            return -1           
        
        if len(self.equipement_domotique) == 0:
            self.logger.warning ("No devices in typologie. Can't start")        
            return -1

        if self.typo_scenario.Setup () == -1:
            self.logger.info ("equipement_pilote :{0} initialization error".format(self.equipement_pilote_id))    
            return -1

        self.typo_scenario.Init (val)
        return 1            