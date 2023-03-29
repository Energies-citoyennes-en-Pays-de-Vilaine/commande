from pgsql import pgsql
import config
import json
import time
import datetime

class Device ():
    def __init__(self):
        self.database = pgsql ()
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

    def SetEquipementDomotiqueId (self, id):
        self.equipement_domotique_id = id
    
    def SetEquipementPiloteOuMesureId(self, id):
        self.equipement_pilote_ou_mesure_id = id
        
    def SetDeviceInfo (self, deviceinfo):
        self.deviceinfo = deviceinfo

    def SetBroker (self, broker):
        self.broker = broker

    def incomingMessage (self, mqtt, devicetype, device, topic, payload):
        pass
    
    def outgoingMessage(self):
        pass
    
    def ems_callback (self, topic, payload):
        pass

    def getUserFromEquipment (self, id_materiel):
        equipement = self.database.select_query ("SELECT utilisateur, utilisateur_affecte "
                                                "FROM {0} "
                                                "WHERE id_materiel='{1}';".
                                                    format (self.config.config['coordination']['equipement_domotique_table'],
                                                    id_materiel.upper()
                                                    )
                                                )
        if len(equipement) > 0:
            return equipement[0][0]
        else:
            return ""
    
    def getEquipementFromUser (self, user):
        devices = self.database.select_query ("SELECT id, equipement_pilote_ou_mesure_id, equipement_domotique_type_id, equipement_domotique_usage_id, id_materiel, marque, utilisateur, utilisateur_affecte, equipement_domotique_specifique_id "
                                                "FROM {0} "
                                                "WHERE utilisateur='{1}';".
                                                    format (self.config.config['coordination']['equipement_domotique_table'],
                                                    user
                                                    )
                                                )
        return devices

    def getEquipementPiloteFromUserUsage (self, user, screen, button):
        equipement_pilote=[]
        assoc = self.config.config['coordination']['screen_usage_assoc']
        print (screen, str(screen), assoc)
        if str(screen) in assoc:
            print ("search equipement for screen", assoc[str(screen)])
            equipement_pilote = self.database.select_query(
                "SELECT id, equipement_pilote_specifique_id, typologie_installation_domotique_id, nom_humain, description, "
                "equipement_pilote_ou_mesure_type_id, equipement_pilote_ou_mesure_mode_id, etat_controle_id, etat_commande_id, "
                "ems_consigne_marche, timestamp_derniere_mise_en_marche, timestamp_derniere_programmation, utilisateur "
                " FROM {0} "
                "where utilisateur = '{1}' and typologie_installation_domotique_id={2}".
                format (
                    self.config.config['coordination']['equipement_pilote_ou_mesure_table'],
                    user,
                    assoc[str(screen)]
                ), 
                self.config.config['coordination']['database'])      
                
        return equipement_pilote

    def getDeviceFromUserUsage (self, user, screen, button):
        device=[]
        assoc = self.config.config['coordination']['screen_usage_assoc']
        if str(screen) in assoc:
                device = self.database.select_query ("SELECT id, equipement_pilote_ou_mesure_id, equipement_domotique_type_id, equipement_domotique_usage_id, id_materiel, marque, utilisateur, utilisateur_affecte, equipement_domotique_specifique_id "
                                                "FROM {0} "
                                                "WHERE utilisateur='{1}' and equipement_domotique_usage_id={2};".
                                                    format (self.config.config['coordination']['equipement_domotique_table'],
                                                    user,
                                                    assoc[str(screen)]
                                                    )
                                                )
                return device
        return device

    def getDeviceFromTopic (self, devices, page, button):
        pass
    
    def getTableFromEquipementType (equipement_domotique_type_id):
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

    def GetHourMinuteFromTimestamp (tstamp):
        dt = datetime.datetime.fromtimestamp(timestamp)
       
        return dt.hour, dt.minute

    def prochain_horaire(horaire):
        heure, minute = map(int, horaire.split(":"))
        maintenant = time.localtime()
        annee, mois, jour, heure_actuelle, minute_actuelle, seconde, jour_de_l_an, jour_de_la_semaine, fuseau_horaire = maintenant
        timestamp_horaire = time.mktime((annee, mois, jour, heure, minute, 0, jour_de_l_an, jour_de_la_semaine, fuseau_horaire))
        if timestamp_horaire < time.mktime(maintenant):
            # le prochain horaire est le lendemain
            timestamp_horaire += 24 * 60 * 60
        return timestamp_horaire
    def GetEndTimestampFromEquipement (equipement_pilote_ou_mesure_id):
        


    def execDeviceAction (self, equipement_pilote_ou_mesure_id, equipement_domotique_type_id, payload):
        action = json.loads (payload)

        if "event" in action:
            event = action["event"]
            
            if (event == "down" or event == "up") and "val" in action:

                query = "update {0} set equipement_pilote_ou_mesure_mode_id = {1} where id = {2} and etat_commande_id <> 60 and equipement_pilote_ou_mesure_mode_id in(20,30) ".format(
                self.config.config['coordination']['equipement_pilote_ou_mesure_table'],
                '20' if action["val"] == 0 else '30',   # 30 pilote / 20 manuel
                equipement_pilote_ou_mesure_id
                )   
                
                self.database.update_query (query, self.config.config['coordination']['database'])   
            elif event == "changed" and "val" in action and "text" in action:
                return
                if val == "3":
                    hour = int (action["text"])
                    current = datetime.datetime.fromtimestamp(time.time())
                    next_timestamp = self.prochain_horaire()

        return    
        
    
    def Action (self, commande):
        pass