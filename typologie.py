
class typologie ():
    def __init__ (self, cfg):
        super().__init__(self)
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
        self.devices = []

    #initialize typologie from typologie_id (ie machine_id in ems result)
    def setup (self, machine_id):
        
        # get equipement_pilote    
        equipement_pilote = self.database.select_query("SELECT id, equipement_pilote_specifique_id, typologie_installation_domotique_id, nom_humain, description, equipement_pilote_ou_mesure_type_id, equipement_pilote_ou_mesure_mode_id, etat_controle_id, etat_commande_id, ems_consigne_marche, timestamp_derniere_mise_en_marche, timestamp_derniere_programmation, utilisateur "
            " FROM equipement_pilote_ou_mesure "
            "where id = {0};
            format (
                machine_id
            
            ), 
            self.config.config['coordination']['database'])
        if (len(equipement_pilote) == 0):
            self.logger.warning ("Unknown equipement_pilote with id:{0}".format(self.machine_id))        
            return -1
        elif len(equipement_pilote) > 1):
            self.logger.warning ("multiple equipement_pilote with id:{0} get only first".format(self.machine_id))        
            
        
        self.equipement_pilote = equipement_pilote[0]
        self.typologie_id = self.equipement_pilote[5]
        self.equipement_pilote_id = self.equipement_pilote[0]
        self.logger.debug ("typologie_id:{0}".format(self.typologie_id))    
        
        # get typologie
        typologie = self.database.select_query("SELECT id, nom, nom_humain, description "
            " FROM equipement_pilote_typologie_installation_domotique "
            "where id = {0};
            format (
                self.typologie_id
        ), 
        self.config.config['coordination']['database'])
        
        if (len(typologie) == 0):
            self.logger.warning ("Unknown typologie with id:{0}".format(self.machine_id))        
            return -1
        elif len(typologie) > 1
            self.logger.warning ("Multiple typologie with id:{0}".format(self.machine_id))        

        self.typologie = typologie[0]
        # load devices
        devices = self.database.select_query("SELECT id, equipement_pilote_ou_mesure_id, equipement_domotique_type_id, equipement_domotique_usage_id, id_materiel, marque, utilisateur, utilisateur_affecte, equipement_domotique_specifique_id "

            " FROM equipement_domotique"
            "where equipement_pilote_ou_mesure_id = {0} AND "
            "user = {1}"
            format (
                self.equipement_pilote_id
        ), 
        self.config.config['coordination']['database'])
        