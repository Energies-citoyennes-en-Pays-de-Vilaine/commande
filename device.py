from pgsql import pgsql
import config
import json
import time
import datetime
import logprefix
import logging

TIMESTAMP_15_MINUTE = (15 * 60)
TIMESTAMP_24_HOUR = (24 * 60 * 60)

class Device ():
    def __init__(self, name):
        """
        Constructeur
        """
        self.database = pgsql (name)
        self.config =  config.config.get_current_config ()
        self.database.init (self.config.config['pgsql']['host'], 
                self.config.config['pgsql']['port'], 
                self.config.config['pgsql']['user'], 
                self.config.config['pgsql']['pass'], 
                self.config.config['pgsql']['database'])
        self.deviceinfo = None
        self.broker = None
        self.equipement_domotique_id = -1
        self.equipement_pilote_ou_mesure_id = -1
        self.equipement_domotique = None
        self.logger = logprefix.LogPrefix(name, logging.getLogger())


    def SetEquipementDomotiqueId (self, id):
        self.equipement_domotique_id = id
    
    def GetEquipementDomotiqueId (self):
        return self.equipement_domotique_id

    def SetEquipementPiloteOuMesureId(self, id):
        self.equipement_pilote_ou_mesure_id = id
    
    def GetEquipementPiloteOuMesureId(self):
        return self.equipement_pilote_ou_mesure_id
    
    def SetDeviceInfo (self, deviceinfo):
        self.deviceinfo = deviceinfo

    def SetBroker (self, broker):
        self.broker = broker

    def incomingMessage (self, mqtt, devicetype, device, topic, payload):
        pass
    
    def outgoingMessage(self, topic, payload):
        pass
    
    def ems_callback (self, topic, payload):
        pass
    """
    def getEquipementDomotiqueFromIdMaterial (self, id_materiel):
        

        equipement = self.database.select_query ("SELECT id, equipement_pilote_ou_mesure_id, equipement_domotique_type_id, equipement_domotique_usage_id, id_materiel, marque, utilisateur, utilisateur_affecte, equipement_domotique_specifique_id "
                                                "FROM {0} "
                                                "WHERE id_materiel='{1}' and utilisateur_affecte = true;".
                                                    format (self.config.config['coordination']['equipement_domotique_table'],
                                                    id_materiel.upper()
                                                    )
                                                )
        if len(equipement) > 0:
            return equipement[0]
        else:
            return None
    """   
    def getUserFromEquipment (self, id_materiel):
        equipement = self.database.select_query ("SELECT utilisateur, utilisateur_affecte "
                                                "FROM {0} "
                                                "WHERE LOWER(id_materiel)=LOWER('{1}') and utilisateur_affecte = true;".
                                                    format (self.config.config['coordination']['equipement_domotique_table'],
                                                    id_materiel.upper()
                                                    )
                                                )
        if len(equipement) > 0:
            return equipement[0][0]
        else:
            return ""
    
    def setCycleDelayFromEquipementPilote (self, equipement_pilote_id, delay):
        query = "update {0} set duree_cycle = {3}" \
            "from "\
	        "{1} " \
            "where " \
	        "{0}.equipement_pilote_machine_generique_id  = {1}.id and " \
	        "{0}.id = {1}.cycle_equipement_pilote_machine_generique_id and " \
	        "{1}.equipement_pilote_ou_mesure_id = {2} ".format( \
                    self.config.config['coordination']['equipement_pilote_machine_generique_cycle'], \
                    self.config.config['coordination']['equipement_pilote_machine_generique'], \
                    equipement_pilote_id, \
                    delay
            )
        return self.database.update_query (query, self.config.config['coordination']['database'])
    
    def getCycleDelayFromEquipementPilote (self, equipement_pilote_id):
        delay = 0
        data = self.database.select_query( \
            "select {0}.duree_cycle " \
            "from "\
	        "{0}, "\
	        "{1} " \
            "where " \
	        "{0}.equipement_pilote_machine_generique_id  = {1}.id and " \
	        "{0}.id = {1}.cycle_equipement_pilote_machine_generique_id and " \
	        "{1}.equipement_pilote_ou_mesure_id = {2} ".format( \
                    self.config.config['coordination']['equipement_pilote_machine_generique_cycle'], \
                    self.config.config['coordination']['equipement_pilote_machine_generique'], \
                    equipement_pilote_id \
            ))
        
        if len(data) > 0:
            delay = data[0][0]
        return delay

    def getDomotiqueDeviceListFromUser (self, user, device_type, material_id):
        devices=[]
        data = self.database.select_query (\
            "select {0}.id, {0}.equipement_pilote_ou_mesure_id " \
            "from " \
            "{0} " \
            "where " \
            "{0}.utilisateur  = '{2}' and " \
            "{0}.equipement_domotique_type_id = {3} and " \
            "LOWER({0}.id_materiel) =  LOWER('{1}') and " \
            "{0}.utilisateur_affecte = TRUE" .format ( \
            self.config.config['coordination']['equipement_domotique_table'],
            material_id,
            user,
            device_type
            )
            )
        
        if len(data) > 0:
            devices = data
        return data
    
    
    def getEquipementFromMaterial_id (self, material_id):
        devices = self.database.select_query ("SELECT id, equipement_pilote_ou_mesure_id, equipement_domotique_type_id, equipement_domotique_usage_id, id_materiel, marque, utilisateur, utilisateur_affecte, equipement_domotique_specifique_id "
                                                "FROM {0} "
                                                "WHERE id_materiel='{1}' and utilisateur_affecte = true;".
                                                    format (self.config.config['coordination']['equipement_domotique_table'],
                                                    material_id.upper()
                                                    )
                                                )
        if len(devices) > 0:
            return devices[0]
        return None
    
    def getEquipementFromUser (self, user):
        devices = self.database.select_query ("SELECT id, equipement_pilote_ou_mesure_id, equipement_domotique_type_id, equipement_domotique_usage_id, id_materiel, marque, utilisateur, utilisateur_affecte, equipement_domotique_specifique_id "
                                                "FROM {0} "
                                                "WHERE utilisateur='{1}' and utilisateur_affecte = true;".
                                                    format (self.config.config['coordination']['equipement_domotique_table'],
                                                    user
                                                    )
                                                )
        return devices
    def GetDeviceInfoFromType (self, device_type_id, device_id):
        devicetype = self.database.select_query("SELECT id, nom "
            "from {0} "
            "where id= {1};".format (
            self.config.config['coordination']['equipement_domotique_type_table'],
            device_type_id))

        if len(devicetype) == 0:
            self.logger.warning("No equipement_domotique_type for id={0}".format(device_type_id))     
            return None

        table = "{0}{1}".format(self.config.config['coordination']['equipement_domotique_table_root'], 
                                            devicetype[0][1])
        query = ""                                            
        if device_type_id == 411:
            # exception sur le nom de colonne topic_mqtt_controle_et_mesure_json pour le type 411
            query = "SELECT id, equipement_domotique_id, topic_mqtt_controle_et_mesure_json, topic_mqtt_commande_json, topic_mqtt_lwt FROM {0} WHERE id={1}".format (table,
                device_id)
        else:
            query = "SELECT id, equipement_domotique_id, topic_mqtt_controle_json, topic_mqtt_commande_text, topic_mqtt_lwt FROM {0} WHERE id={1}".format (table,
                device_id)

        deviceinfo = self.database.select_query(query)
            
        self.logger.debug ("device info:{0}".format(deviceinfo))   
        if len(deviceinfo) == 0:
            return None
        #print (deviceinfo[0])
        return deviceinfo[0]
    
    def GetEquipementPiloteFromId (self, equipement_pilote_ou_mesure_id):
        equipement_pilote = self.database.select_query(
                "SELECT id, equipement_pilote_specifique_id, typologie_installation_domotique_id, nom_humain, description, "
                "equipement_pilote_ou_mesure_type_id, equipement_pilote_ou_mesure_mode_id, etat_controle_id, etat_commande_id, "
                "ems_consigne_marche, timestamp_derniere_mise_en_marche, timestamp_derniere_programmation, utilisateur "
                " FROM {0} "
                "where id = {1}".
                format (
                    self.config.config['coordination']['equipement_pilote_ou_mesure_table'],
                    equipement_pilote_ou_mesure_id
                ), 
                self.config.config['coordination']['database'])      
        if len(equipement_pilote) > 0:
            return equipement_pilote[0]
        
        return None
    
    def getEquipementPiloteFromUserUsageType (self, user, screen, button):
        equipement_pilote=[]
        assoc = self.config.config['coordination']['screen_usage_assoc']
        #print (screen, str(screen), assoc)
        if str(screen) in assoc:
            #print ("search equipement_pilote for screen:", assoc[str(screen)])
            equipement_pilote = self.database.select_query(
                "SELECT id, equipement_pilote_specifique_id, typologie_installation_domotique_id, nom_humain, description, "
                "equipement_pilote_ou_mesure_type_id, equipement_pilote_ou_mesure_mode_id, etat_controle_id, etat_commande_id, "
                "ems_consigne_marche, timestamp_derniere_mise_en_marche, timestamp_derniere_programmation, utilisateur "
                " FROM {0} "
                "where utilisateur = '{1}' and equipement_pilote_ou_mesure_type_id in {2}".
                format (
                    self.config.config['coordination']['equipement_pilote_ou_mesure_table'],
                    user,
                    '(' + ','.join(map(str, assoc[str(screen)])) + ')'
                ), 
                self.config.config['coordination']['database'])      
                
        return equipement_pilote
    
    def GetEquipementPiloteFromUser (self, user):
        equipement_pilote = self.database.select_query(
                "SELECT id, equipement_pilote_specifique_id, typologie_installation_domotique_id, nom_humain, description, "
                "equipement_pilote_ou_mesure_type_id, equipement_pilote_ou_mesure_mode_id, etat_controle_id, etat_commande_id, "
                "ems_consigne_marche, timestamp_derniere_mise_en_marche, timestamp_derniere_programmation, utilisateur "
                " FROM {0} "
                "where utilisateur = '{1}'".
                format (
                    self.config.config['coordination']['equipement_pilote_ou_mesure_table'],
                    user
                ), 
                self.config.config['coordination']['database'])   
        return equipement_pilote
    
    
    def getEquipementPiloteFromUserUsage (self, user, screen, button):
        equipement_pilote=[]
        assoc = self.config.config['coordination']['screen_usage_assoc']
        #print (screen, str(screen), assoc)
        if str(screen) in assoc:
            #print ("search equipement for screen", assoc[str(screen)])
            equipement_pilote = self.database.select_query(
                "SELECT id, equipement_pilote_specifique_id, typologie_installation_domotique_id, nom_humain, description, "
                "equipement_pilote_ou_mesure_type_id, equipement_pilote_ou_mesure_mode_id, etat_controle_id, etat_commande_id, "
                "ems_consigne_marche, timestamp_derniere_mise_en_marche, timestamp_derniere_programmation, utilisateur "
                " FROM {0} "
                "where utilisateur = '{1}' and typologie_installation_domotique_id in {2}".
                format (
                    self.config.config['coordination']['equipement_pilote_ou_mesure_table'],
                    user,
                    '(' + ','.join(map(str, assoc[str(screen)])) + ')'
                ), 
                self.config.config['coordination']['database'])      
                
        return equipement_pilote
   
    def getDeviceFromTopic (self, devices, page, button):
        pass
    
    def GetEquipementPiloteMode (self, equipement_pilote_ou_mesure_id):
        mode = -1
        data = self.database.select_query (
            "select equipement_pilote_ou_mesure_mode_id " \
            "from {0} "
            "where id = {1} and etat_controle_id <> 60 ".format( 
                    self.config.config['coordination']['equipement_pilote_ou_mesure_table'],  
                    equipement_pilote_ou_mesure_id 
                    ) 
        )

        if len(data) > 0:
            mode = data[0][0]
        return mode
    
    def UpdateEquipementPiloteMode(self, mode, equipement_pilote_ou_mesure_id):
        """
        Met à jour le mode et la date d'activation de l'equipement

        arguments:
        mode    mode de l'equipement 0 = mode manuel / 1 mode auto
        """
        query = "update {0} set equipement_pilote_ou_mesure_mode_id = {1} " \
            "where id = {2} and etat_controle_id <> 60 and " \
            "equipement_pilote_ou_mesure_mode_id in(20,30,70) ".format( 
                    self.config.config['coordination']['equipement_pilote_ou_mesure_table'], 
                    mode,   
                    equipement_pilote_ou_mesure_id 
                    )   
        
        if self.database.update_query (query, self.config.config['coordination']['database']) > 0 :
            return 1
        return 0

    def getTableFromEquipementType (self, equipement_domotique_type_id):
        """
        Build database table name from equipement_domotique type

        Args:
            equipement_domotique_type_id (Integer): equipement_domotique ident

        Returns:
            String: database table
        """
        table = ""
        data = self.database.select_query ("SELECT nom, FROM {0} "
                                                "WHERE equipement_domotique_type_id={1};".
                                                    format (self.config.config['coordination']['equipement_domotique_type_table'],
                                                    equipement_domotique_type_id,
                                                    
                                                    )
                                                )
        if len(data) == 1:
            table = data[0][0]
        return table

    def GetHourMinuteFromTimestamp (self, tstamp):
        """
        Compute Hour and Minute of a timestamp

        Args:
            tstamp (timestamp): Date / time

        Returns:
            Number, Number: Hour and Minute
        """
        dt = datetime.datetime.fromtimestamp(tstamp)
       
        return dt.hour, dt.minute

    def prochain_horaire(self, horaire):
        """_summary_

        Args:
            horaire (string): hour string (hh:mm)

        Returns:
            timestamp: the timestamp of the next "horaire" 
        """
        heure, minute = map(int, horaire.split(":"))
        maintenant = time.localtime()
        annee, mois, jour, heure_actuelle, minute_actuelle, seconde, jour_de_l_an, jour_de_la_semaine, fuseau_horaire = maintenant
        timestamp_horaire = time.mktime((annee, mois, jour, heure, minute, 0, jour_de_l_an, jour_de_la_semaine, fuseau_horaire))
        if timestamp_horaire < time.mktime(maintenant):
            # le prochain horaire est le lendemain
            timestamp_horaire += TIMESTAMP_24_HOUR
        return timestamp_horaire
    
    def next_timestamp_horaire (self, tstamp):
        """
        Compute the same device programmation hour in the next 24 Hour

        Args:
            tstamp (timestamp): timestamp

        Returns:
            timestamp: same device programmation hour in the next 24 Hour
        """
        now = time.time ()
        tstamp = (tstamp // TIMESTAMP_15_MINUTE) * TIMESTAMP_15_MINUTE
        while tstamp < now:
            tstamp += TIMESTAMP_24_HOUR
        return tstamp
    
    def UpdateActivationTime (self, equipement_pilote_ou_mesure_id, tstamp):
        """
        Update timestamp_derniere_mise_en_marche in equipement_pilote_ou_mesure table

        Args:
            equipement_pilote_ou_mesure_id (_type_): equipement_pilote_ou_mesure ident
            tstamp (_type_): timestamp
        """
        query = "update {0} set timestamp_derniere_mise_en_marche = {1} where id = {2} and etat_controle_id <> 60 and equipement_pilote_ou_mesure_mode_id in(20,30) ".format(
                                                self.config.config['coordination']['equipement_pilote_ou_mesure_table'],
                                                tstamp,   
                                                equipement_pilote_ou_mesure_id
                                                )  
        self.database.update_query (query, self.config.config['coordination']['database'])

    def UpdateProgrammationTime (self, equipement_pilote_ou_mesure_id, tstamp):
        """
        Update timestamp_derniere_programmation in equipement_pilote_ou_mesure table

        Args:
            equipement_pilote_ou_mesure_id (integer): equipement_pilote_ou_mesure ident
            tstamp (timestamp): timestamp
        """
        query = "update {0} set timestamp_derniere_programmation = {1} where id = {2} and etat_controle_id <> 60 and equipement_pilote_ou_mesure_mode_id in(20,30) ".format(
                                                self.config.config['coordination']['equipement_pilote_ou_mesure_table'],
                                                tstamp,   
                                                equipement_pilote_ou_mesure_id
                                                )  
        self.database.update_query (query, self.config.config['coordination']['database'])

    def SetEndTimestampFromEquipement (self, equipement_pilote_ou_mesure_id, tstamp):
        query = "UPDATE {0} SET timestamp_de_fin_souhaite = {1} WHERE equipement_pilote_ou_mesure_id = {2};".format (
                    self.config.config['coordination']['equipement_pilote_machine_generique'],
                    tstamp,
                    equipement_pilote_ou_mesure_id
                )
        data = self.database.update_query (query)

    def SetEndTimestampFromEquipementVoiture (self, equipement_pilote_ou_mesure_id, tstamp):
        query = "UPDATE {0} SET timestamp_dispo_souhaitee = {1} WHERE equipement_pilote_ou_mesure_id = {2};".format (
                    self.config.config['coordination']['equipement_pilote_vehicule_electrique_generique'],
                    tstamp,
                    equipement_pilote_ou_mesure_id
                )
        data = self.database.update_query (query)

    def SetPendingLoadFromEquipement (self, equipement_pilote_ou_mesure_id, pendingload):
        query = "UPDATE {0} SET pourcentage_charge_restant = {1} WHERE equipement_pilote_ou_mesure_id = {2};".format (
                    self.config.config['coordination']['equipement_pilote_vehicule_electrique_generique'],
                    pendingload,
                    equipement_pilote_ou_mesure_id
                )
        data = self.database.update_query (query)

    def GetPendingLoadFromEquipement (self, equipement_pilote_ou_mesure_id):
        data = self.database.select_query ("SELECT pourcentage_charge_restant FROM {0} WHERE equipement_pilote_ou_mesure_id = {1};".format (
                    self.config.config['coordination']['equipement_pilote_vehicule_electrique_generique'],
                    equipement_pilote_ou_mesure_id
                )
        )
        if len(data) > 0:
            return data[0][0]
        return 0
    
    def GetEndTimestampFromEquipement (self, equipement_pilote_ou_mesure_id):
        data = self.database.select_query ('SELECT id, equipement_pilote_ou_mesure_id, timestamp_de_fin_souhaite, '
                'delai_attente_maximale_apres_fin, cycle_equipement_pilote_machine_generique_id, '
                'mesures_puissance_elec_id '
                'FROM {0} '
                'WHERE equipement_pilote_ou_mesure_id = {1}'. format (
                        self.config.config['coordination']['equipement_pilote_machine_generique'],
                        equipement_pilote_ou_mesure_id
                    )
                )
        if len(data) > 0:
            return data[0][2]
        return 0

    def GetEndTimestampFromEquipementVoiture (self, equipement_pilote_ou_mesure_id):
        data = self.database.select_query ('SELECT id, equipement_pilote_ou_mesure_id, pourcentage_charge_restant, '
                'pourcentage_charge_finale_minimale_souhaitee, duree_de_charge_estimee, timestamp_dispo_souhaitee,  ' 
                'puissance_de_charge, capacite_de_batterie, mesures_puissance_elec_id '
                'FROM {0} '
                'WHERE equipement_pilote_ou_mesure_id = {1};'. format (
                        self.config.config['coordination']['equipement_pilote_vehicule_electrique_generique'],
                        equipement_pilote_ou_mesure_id
                    )
                )
        if len(data) > 0:
            return data[0][5]
        return 0        
          
    
    def Action (self, commande, equipement_pilote_ou_mesure_id):
        pass