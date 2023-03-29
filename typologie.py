import paho.mqtt.client as broker
import threading
import datetime
import config
import logging
import time
import pgsql
import typologiescenario_factory



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
    def Setup (self, machine_id):
        
        # get equipement_pilote    
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
            return -1
        elif len(equipement_pilote) > 1:
            self.logger.warning ("multiple equipement_pilote with id:{0} get only first".format(machine_id))        
        
        
        self.machine_id = machine_id    
        self.equipement_pilote = equipement_pilote[0]
        self.typologie_type_id = self.equipement_pilote[2]
        self.equipement_pilote_id = self.equipement_pilote[0]
        self.logger.debug ("typologie_type_id:{0}".format(self.typologie_type_id))    
        
        

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

    def Start (self):
        if self.typo_scenario == None:
            self.logger.warning ("unknown typologie")        
            return -1           
        if len(self.equipement_domotique) == 0:
            self.logger.warning ("No devices in typologie. Can't start")        
            return  -1
        if self.equipement_pilote[6] != 30:
            self.logger.info ("equipement_pilote :{0} n'est pas en mode pilote".format(self.equipement_pilote_id))    
            return;
        self.typo_scenario.Setup ()    
        self.typo_scenario.Run ()
                             