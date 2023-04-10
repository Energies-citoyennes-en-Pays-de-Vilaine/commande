import logging
import elfeconstant
from typologiescenario_switch import TypologieScenarioSwitch
from typologiescenario_plug import TypologieScenarioPlug
from typologiescenario_relaicompteur import TypologieScenarioRelaiCompteur

class TypologieScenarioFactory ():
    def __init__(self):
        pass

    def CreateScenario (self, typologie_id, config, equipement_pilote_ou_mesure_id, equipement_domotiques, broker):
        scenario = None
        if typologie_id == elfeconstant.TYPOLOGIE_PRISE_ET_DOIGT:
            scenario = TypologieScenarioSwitch (config, equipement_pilote_ou_mesure_id,
                        equipement_domotiques, broker)

        elif typologie_id == elfeconstant.TYPOLOGIE_PRISE:
            scenario = TypologieScenarioPlug (config, equipement_pilote_ou_mesure_id,
                        equipement_domotiques, broker)

        elif typologie_id == elfeconstant.TYPOLOGIE_RELAI_COMPTEUR:
            scenario = TypologieScenarioRelaiCompteur (config, equipement_pilote_ou_mesure_id,
                        equipement_domotiques, broker)

        else:
            logging.getLogger().warning("Unknown typologie scenario for id:{0}".format (typologie_id))
            return None

        logging.getLogger().info ("Created typologie {}".format(type(scenario)))
        return scenario