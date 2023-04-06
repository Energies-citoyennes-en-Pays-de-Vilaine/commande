import logging
from  typologiescenario_switch import TypologieScenarioSwitch
from  typologiescenario_plug import TypologieScenarioPlug

class TypologieScenarioFactory ():
    def __init__(self):
        pass

    def CreateScenario (self, typologie_id, config, equipement_pilote_ou_mesure_id, equipement_domotiques, broker):
        if typologie_id == 130:
            logging.getLogger().info ("Creating typologie {}".format("TypologieScenarioSwitch"))
            return TypologieScenarioSwitch (config, equipement_pilote_ou_mesure_id,
                        equipement_domotiques, broker)
        elif typologie_id == 120:
            logging.getLogger().info ("Creating typologie {}".format("TypologieScenarioPlug"))
            return TypologieScenarioPlug (config, equipement_pilote_ou_mesure_id,
                        equipement_domotiques, broker)
        else:
            logging.getLogger().warning("Unknown typologie scenario for id:{0}".format (typologie_id))
            return None