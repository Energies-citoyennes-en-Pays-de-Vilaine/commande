from typologiescenario import TypologieScenario
import logging

class TypologieScenarioSwitch (TypologieScenario):
    def __init__(self, cfg, equipement_pilote_ou_mesure_id, equipement_domotique, broker):
        super().__init__(cfg, equipement_pilote_ou_mesure_id, equipement_domotique, broker)
        
    
        

    def Run (self):
        device_demarrage = 32
        logging.getLogger().info ("Get device type {0} for start".format(device_demarrage))

        if device_demarrage in self.equipement_domotique_usage :    
            print (self.equipement_domotique_usage[device_demarrage])
            self.equipement_domotique_usage[device_demarrage].Action ("ON", self.equipement_pilote_ou_mesure_id)
        else:
            logging.getLogger().warning ("Unknown device for usage {0}".format(device_demarrage))