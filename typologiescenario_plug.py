from typologiescenario import TypologieScenario
import logging
import elfeconstant
import logprefix

class TypologieScenarioPlug (TypologieScenario):
    def __init__(self, cfg, equipement_pilote_ou_mesure_id, equipement_domotique, broker):
        """
        Constructeur
        
        """
        super().__init__(cfg, equipement_pilote_ou_mesure_id, equipement_domotique, broker, __name__)
        self.inverse = False
        

    def setInverse (self, inverse):
        self.inverse = inverse

    def Run (self, continuous, ems_consign):
        """
        Demarre une typologie sur instruction EMS   

        arguments:
        continuous      0 la typologie est en mode normal / 1 la typologie est en mode continu
        ems_consign     0 la typologie doit etre desactive (off) / 1 la typologie doit etre activée (ON)
        """
        device_demarrage = elfeconstant.USAGE_MESURE_ELEC_COMMUTER
        action_on = elfeconstant.DEVICE_ACTION_ON
        action_off = elfeconstant.DEVICE_ACTION_OFF

        if self.inverse:
            action_on = elfeconstant.DEVICE_ACTION_OFF
            action_off = elfeconstant.DEVICE_ACTION_ON

        self.logger.info ("Get equipement_domotique type: {0} for action in mode {1}".format(device_demarrage, "normal" if continuous == 0 else "continu"))

        if device_demarrage in self.equipement_domotique_usage :    
            if continuous == 0:
                #si la consigne est à 0,on renvoie un ordre OFF
                if ems_consign == 0:
                    self.equipement_domotique_usage[device_demarrage].Action (action_off, self.equipement_pilote_ou_mesure_id)
                #sinon, alors on demarre l'equipement domotique et on repasse l'equipement piloté en manuel
                elif self.equipement_domotique_usage[device_demarrage].Action (action_on, self.equipement_pilote_ou_mesure_id) == 1:
                    #passage en mode manuel
                    self.UpdateModePiloteManuel(0, False) 
                    self.SetEtatCommandeId (self.equipement_pilote_ou_mesure_id, elfeconstant.COMMAND_ON)
                    self.SetEtatControleId (self.equipement_pilote_ou_mesure_id, elfeconstant.CONTROLE_ON)
                    self.SetEmsConsigneMarche (self.equipement_pilote_ou_mesure_id, True)
                else:
                    # TODO: Gerer le cas d'erreur
                    self.logger.warning ("command failed for equipement_id {0}".format(self.equipement_pilote_ou_mesure_id))
                    #update mode pilote / manuel
                    self.UpdateModePiloteManuel(0, False) 
                    self.SetEmsConsigneMarche (self.equipement_pilote_ou_mesure_id, True)
            else:
                #on demarre l'equipement domotique en fonction de la consigne de l'ems
                if ems_consign != 0:
                    self.equipement_domotique_usage[device_demarrage].Action (action_on, self.equipement_pilote_ou_mesure_id)
                    self.SetEtatCommandeId (self.equipement_pilote_ou_mesure_id, elfeconstant.COMMAND_ON)
                    self.SetEtatControleId (self.equipement_pilote_ou_mesure_id, elfeconstant.CONTROLE_ON)
                    self.SetEmsConsigneMarche (self.equipement_pilote_ou_mesure_id, True)
                else:
                    self.equipement_domotique_usage[device_demarrage].Action (action_off, self.equipement_pilote_ou_mesure_id)
                    self.SetEtatCommandeId (self.equipement_pilote_ou_mesure_id, elfeconstant.COMMAND_WAIT_ON)
                    self.SetEtatControleId (self.equipement_pilote_ou_mesure_id, elfeconstant.CONTROLE_OFF)
                    self.SetEmsConsigneMarche (self.equipement_pilote_ou_mesure_id, False)
                # TODO: Gerer le cas d'erreur
        else:
            self.logger.warning ("Unknown device for usage {0}".format(device_demarrage))
    
    def Init (self, val):
        """
        Demarre une typologie sur passage manuel / pilote  par une IHM          

        arguments:
        val     0 mode manuel / 1 mode pilote
        """

        device_demarrage = elfeconstant.USAGE_MESURE_ELEC_COMMUTER
        action_on = elfeconstant.DEVICE_ACTION_ON
        action_off = elfeconstant.DEVICE_ACTION_OFF

        if self.inverse:
            action_on = elfeconstant.DEVICE_ACTION_OFF
            action_off = elfeconstant.DEVICE_ACTION_ON
        self.logger.info ("Get device type {0} for init mode={1}".format(device_demarrage, val))


        if device_demarrage in self.equipement_domotique_usage :    
            if not val in (0,1):
                logging.getLogger().warning ("Unknown Action for device type {0}".format(device_demarrage))    
                return

            result = -1
            if val == 0: # passage en mode manuel on passe le device a ON
                result = self.equipement_domotique_usage[device_demarrage].Action (action_on, self.equipement_pilote_ou_mesure_id)
                self.SetEtatCommandeId (self.equipement_pilote_ou_mesure_id, elfeconstant.COMMAND_ON)
                self.SetEtatControleId (self.equipement_pilote_ou_mesure_id, elfeconstant.CONTROLE_ON)
                self.SetEmsConsigneMarche (self.equipement_pilote_ou_mesure_id, True)
            elif val == 1: # passage en mode auto on passe le device à OFF
                result = self.equipement_domotique_usage[device_demarrage].Action (action_off, self.equipement_pilote_ou_mesure_id)                            
                self.SetEtatCommandeId (self.equipement_pilote_ou_mesure_id, elfeconstant.COMMAND_STANDBY)
                self.SetEtatControleId (self.equipement_pilote_ou_mesure_id, elfeconstant.CONTROLE_OFF)
                self.SetEmsConsigneMarche (self.equipement_pilote_ou_mesure_id, False)
            
            if result == 1:
                self.UpdateModePiloteManuel(val) 
            else:
                #TODO: Gerer le cas d'erreur
                self.UpdateModePiloteManuel(val) 

        else:
            self.logger.warning ("Unknown device for usage {0}".format(device_demarrage))
        pass    
