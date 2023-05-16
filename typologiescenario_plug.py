from typologiescenario import TypologieScenario
import logging
import elfeconstant

class TypologieScenarioPlug (TypologieScenario):
    def __init__(self, cfg, equipement_pilote_ou_mesure_id, equipement_domotique, broker):
        """
        Constructeur
        
        """
        super().__init__(cfg, equipement_pilote_ou_mesure_id, equipement_domotique, broker)
        
    def Run (self, continuous, ems_consign):
        """
        Demarre une typologie sur instruction EMS   

        arguments:
        continuous      0 la typologie est en mode normal / 1 la typologie est en mode continu
        ems_consign     0 la typologie doit etre desactive (off) / 1 la typologie doit etre activée (ON)
        """
        device_demarrage = elfeconstant.USAGE_MESURE_ELEC_COMMUTER
        
        logging.getLogger().info ("Get equipement_domotique type: {0} for action in mode {1}".format(device_demarrage, "normal" if continuous == 0 else "continu"))

        if device_demarrage in self.equipement_domotique_usage :    
            if continuous == 0:
                #on demarre l'equipement domotique et on le repasse en manuel
                if self.equipement_domotique_usage[device_demarrage].Action (elfeconstant.DEVICE_ACTION_ON, self.equipement_pilote_ou_mesure_id) == 1:
                    #passage en mode manuel
                    self.UpdateModePiloteManuel(0) 
                    self.SetEtatCommandeId (self.equipement_pilote_ou_mesure_id, elfeconstant.COMMAND_ON)
                    self.SetEtatControleId (self.equipement_pilote_ou_mesure_id, elfeconstant.CONTROLE_ON)
                    self.SetEmsConsigneMarche (self.equipement_pilote_ou_mesure_id, 1)
                else:
                    # TODO: Gerer le cas d'erreur
                    #update mode pilote / manuel
                    self.UpdateModePiloteManuel(0) 
                    self.SetEmsConsigneMarche (self.equipement_pilote_ou_mesure_id, 1)
            else:
                #on demarre l'equipement domotique en fonction de la consigne de l'ems
                if ems_consign != 0:
                    self.equipement_domotique_usage[device_demarrage].Action (elfeconstant.DEVICE_ACTION_ON, self.equipement_pilote_ou_mesure_id)
                    self.SetEtatCommandeId (self.equipement_pilote_ou_mesure_id, elfeconstant.COMMAND_ON)
                    self.SetEtatControleId (self.equipement_pilote_ou_mesure_id, elfeconstant.CONTROLE_ON)
                    self.SetEmsConsigneMarche (self.equipement_pilote_ou_mesure_id, 1)
                else:
                    self.equipement_domotique_usage[device_demarrage].Action (elfeconstant.DEVICE_ACTION_OFF, self.equipement_pilote_ou_mesure_id)
                    self.SetEtatCommandeId (self.equipement_pilote_ou_mesure_id, elfeconstant.COMMAND_WAIT_ON)
                    self.SetEtatControleId (self.equipement_pilote_ou_mesure_id, elfeconstant.CONTROLE_OFF)
                    self.SetEmsConsigneMarche (self.equipement_pilote_ou_mesure_id, 0)
                # TODO: Gerer le cas d'erreur
        else:
            logging.getLogger().warning ("Unknown device for usage {0}".format(device_demarrage))
    
    def Init (self, val):
        """
        Demarre une typologie sur passage manuel / pilote  par une IHM          

        arguments:
        val     0 mode manuel / 1 mode pilote
        """

        device_demarrage = elfeconstant.USAGE_MESURE_ELEC_COMMUTER
        logging.getLogger().info ("Get device type {0} for init mode={1}".format(device_demarrage, val))


        if device_demarrage in self.equipement_domotique_usage :    
            if not val in (0,1):
                logging.getLogger().warning ("Unknown Action for device type {0}".format(device_demarrage))    
                return

            result = -1
            if val == 0: # passage en mode manuel on passe le device a ON
                result = self.equipement_domotique_usage[device_demarrage].Action (elfeconstant.DEVICE_ACTION_ON, self.equipement_pilote_ou_mesure_id)
                self.SetEtatCommandeId (self.equipement_pilote_ou_mesure_id, elfeconstant.COMMAND_ON)
                self.SetEtatControleId (self.equipement_pilote_ou_mesure_id, elfeconstant.CONTROLE_ON)
            elif val == 1: # passage en mode auto on passe le device à OFF
                result = self.equipement_domotique_usage[device_demarrage].Action (elfeconstant.DEVICE_ACTION_OFF, self.equipement_pilote_ou_mesure_id)                            
                self.SetEtatCommandeId (self.equipement_pilote_ou_mesure_id, elfeconstant.COMMAND_STANDBY)
                self.SetEtatControleId (self.equipement_pilote_ou_mesure_id, elfeconstant.CONTROLE_OFF)
            
            if result == 1:
                self.UpdateModePiloteManuel(val) 
            else:
                #TODO: Gerer le cas d'erreur
                self.UpdateModePiloteManuel(val) 
            
            
        else:
            logging.getLogger().warning ("Unknown device for usage {0}".format(device_demarrage))
        pass    