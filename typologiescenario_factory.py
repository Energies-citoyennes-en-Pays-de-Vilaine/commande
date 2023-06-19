import logging
import elfeconstant
import logprefix
from typologiescenario_switch import TypologieScenarioSwitch
from typologiescenario_plug import TypologieScenarioPlug
from typologiescenario_relaicompteur import TypologieScenarioRelaiCompteur
from typologiescenario_relaicapteur import TypologieScenarioRelaiCapteur
from typologiescenario_prisedeuxdoigts import TypologieScenarioPrise2Doigts
from typologiescenario_doubleappui import TypologieScenarioDoubleAppui

class TypologieScenarioFactory ():
    def __init__(self):
        """
        Constructeur
        """
        self.logger = logprefix.LogPrefix(__name__, logging.getLogger())

    def CreateScenario (self, typologie_id, config, equipement_pilote_ou_mesure_id, equipement_domotiques, broker):
        """
        Crée une typologie

        arguments:
        typologie id                    identifiant de typologie
        config                          singleton de configuration
        equipement_pilote_ou_mesure_id  id de l'equipement_domotique
        equipement_domotiques           liste des equipements domotiques associés
        broker                          reference à l'ems_broker
        """
        scenario = None
        if typologie_id == elfeconstant.TYPOLOGIE_PRISE_ET_DOIGT:
            scenario = TypologieScenarioSwitch (config, equipement_pilote_ou_mesure_id,
                        equipement_domotiques, broker)
        
        elif typologie_id == elfeconstant.TYPOLOGIE_PRISE_DOIGT_DOUBLE:
            scenario = TypologieScenarioDoubleAppui (config, equipement_pilote_ou_mesure_id,
                        equipement_domotiques, broker)
        
        elif typologie_id == elfeconstant.TYPOLOGIE_PRISE_ET_DEUX_DOIGT:
            scenario = TypologieScenarioPrise2Doigts (config, equipement_pilote_ou_mesure_id,
                        equipement_domotiques, broker)
        
        elif typologie_id == elfeconstant.TYPOLOGIE_PRISE:
            scenario = TypologieScenarioPlug (config, equipement_pilote_ou_mesure_id,
                        equipement_domotiques, broker)
            
        elif typologie_id == elfeconstant.TYPOLOGIE_PRISE_INVERSE:
            scenario = TypologieScenarioPlug (config, equipement_pilote_ou_mesure_id,
                        equipement_domotiques, broker)
            scenario.setInverse (True)
            
        elif typologie_id == elfeconstant.TYPOLOGIE_RELAI_COMPTEUR:
            scenario = TypologieScenarioRelaiCompteur (config, equipement_pilote_ou_mesure_id,
                        equipement_domotiques, broker)
            
        elif typologie_id == elfeconstant.TYPOLOGIE_RELAI_ET_CAPTEUR:
            scenario = TypologieScenarioRelaiCapteur (config, equipement_pilote_ou_mesure_id,
                        equipement_domotiques, broker)
        else:
            self.logger.warning("Unknown typologie scenario for id:{0}".format (typologie_id))
            return None

        self.logger.info ("Created typologie {}".format(type(scenario)))
        return scenario