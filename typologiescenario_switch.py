from typologiescenario import TypologieScenario
import logging
import elfeconstant

class TypologieScenarioSwitch (TypologieScenario):
    def __init__(self, cfg, equipement_pilote_ou_mesure_id, equipement_domotique, broker):
        super().__init__(cfg, equipement_pilote_ou_mesure_id, equipement_domotique, broker)
    
    def Run (self, continuous, ems_consign):
        """
        Demarre une typologie sur instruction EMS   

        arguments:
        continuous      0 la typologie est en mode normal / 1 la typologie est en mode continu
        ems_consign     0 la typologie doit etre desactive (off) / 1 la typologie doit etre activée (ON)
        """
        device_demarrage = elfeconstant.USAGE_APPUYER_DEMARRAGE
        logging.getLogger().info ("Get equipement_domotique type {0} for start".format(device_demarrage))

        if device_demarrage in self.equipement_domotique_usage :    
            if continuous == 0:
                #on demarre l'equipement domotique et on le repasse en manuel
                result = self.equipement_domotique_usage[device_demarrage].Action (elfeconstant.DEVICE_ACTION_ON, self.equipement_pilote_ou_mesure_id)

                if result == 1:
                    #passage en mode manuel
                    self.UpdateModePiloteManuel(0) 
                else:
                    # TODO: Gerer le cas d'erreur
                    #update mode pilote / manuel
                    self.UpdateModePiloteManuel(0) 
            else:
                if ems_consign != 0:
                    # TODO: Gerer le cas d'erreur
                    result = self.equipement_domotique_usage[device_demarrage].Action (elfeconstant.DEVICE_ACTION_ON, self.equipement_pilote_ou_mesure_id)
                else:
                    logging.getLogger().info ("equipement_domotique type {0} can't handle OFF".format(device_demarrage))
                    
        else:
            logging.getLogger().warning ("Unknown device for usage {0}".format(device_demarrage))

        

    def Init (self, val):
        """
        Demarre une typologie sur passage manuel / pilote            

        arguments:
        val     0 mode manuel / 1 mode pilote
        """

        # mise à jour du mode en base de données
        self.UpdateModePiloteManuel(val) 
        
