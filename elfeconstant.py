
# varibale d'environnement
ENV_DATABASE_PWD    = "commande_db_pass"
ENV_DATABASE_USER    = "commande_db_user"
ENV_BROKER_PWD      = "commande_broker_pass"
ENV_BROKER_USER      = "commande_broker_user"

# defini le lien avec les typologies de la table "equipement_pilote_typologie_installation_domotique"
TYPOLOGIE_2RELAIS = 110
TYPOLOGIE_PRISE = 120
TYPOLOGIE_PRISE_ET_DOIGT = 130
TYPOLOGIE_RELAI_ET_CAPTEUR = 140
TYPOLOGIE_PRISE_ET_DEUX_DOIGT = 150
TYPOLOGIE_PRISE_DOIGT_DOUBLE = 160
TYPOLOGIE_PRISE_RALLUME_DOIGT = 170
TYPOLOGIE_RELAI_COMPTEUR = 180
TYPOLOGIE_PRISE_INVERSE = 190

# defini le lien avec les usages de la table "equipement_domotique_usage"
USAGE_MESURE_ELEC_COMMUTER = 11
USAGE_COMMUTER = 12
USAGE_MESURE_ELEC = 21
USAGE_APPUYER_POWER = 31
USAGE_APPUYER_DEMARRAGE = 32
USAGE_MESURER_AMBIANCE = 61
USAGE_IHM = 71

#defeini le lien avec equipement_pilote_etat_controle
CONTROLE_ON = 15
CONTROLE_OFF = 25
CONTROLE_ERRCOM = 60
CONTROLE_UNKNOWN = 70

#defini le lien avec equipement_pilote_etat_commande
COMMAND_INITIAL = 1	    #etat_initial
COMMAND_WAIT_ON = 12	#en_attente_on
COMMAND_STANDBY = 11	#pilote_stand_by
COMMAND_ACTIV   = 21	#pilote_en_activation
COMMAND_ON      = 13	#manuel_on
COMMAND_ERR     = 30	#err
COMMAND_NOCMD   = 99	# non_commande


# Action sur les equipement domotique
DEVICE_ACTION_ON = "ON"
DEVICE_ACTION_OFF = "OFF"

# Mode de fonctionnement
EQUIPEMENT_PILOTE_MODE_MANUEL = '20'
EQUIPEMENT_PILOTE_MODE_PILOTE = '30'
EQUIPEMENT_PILOTE_MODE_PILOTE_NUM = 30

#identifiant du type d'ecran
EQUIPEMENT_PILOTE_TYPE_SCREEN = 711

# identifiant des elements sur l'ecran HASP
SCREEN_OBJ_LED = 10
SCREEN_OBJ_TIME_HOUR = 8
SCREEN_OBJ_TIME_MINUTE = 9

SCREEN_OBJ_VOITURE_TIME_HOUR = 5
SCREEN_OBJ_VOITURE_TIME_MINUTE = 6
SCREEN_OBJ_VOITURE_LOAD = 8
SCREEN_OBJ_PILOTE_SWITCH = 3
