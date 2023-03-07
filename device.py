from pgsql import pgsql
import config

class Device ():
    def __init__(self):
        self.database = pgsql ()
        self.config =  config.config.get_current_config ()
        self.database.init (self.config.config['pgsql']['host'], 
                self.config.config['pgsql']['port'], 
                self.config.config['pgsql']['user'], 
                self.config.config['pgsql']['pass'], 
                self.config.config['pgsql']['database'])

    def incomingMessage (self, mqtt, devicetype, device, topic, payload):
        pass
    
    def outgoingMessage(self):
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
                                                "WHERE equipement_domotique_type_id={2};".
                                                    format (self.config.config['coordination']['equipement_domotique_type_table'],
                                                    equipement_domotique_type_id,
                                                    
                                                    )
                                                )
        if len(data) == 1:
            table = data[0][0]
        return table

    def execDeviceAction (equipement_pilote_ou_mesure_id, equipement_domotique_type_id, payload):
        action = json.loads (payload)

        query = "update {0} set etat-commande = {1} where id = {2}".format (
                self.config.config['coordination']['equipement_pilote_ou_mesure_table'],
                12 if action.value == 0 else 22,
                equipement_pilote_ou_mesure_id
                
        )
        self.database.update_query (query, self.config.config['coordination']['database'])