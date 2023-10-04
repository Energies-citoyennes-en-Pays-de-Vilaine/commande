# Projet ELFE - Controle-Commande

## Description
Ce dépôt contient le code nécessaire au contrôle-commande des équipements domotiques déployés dans le projet ELFE. 
Très basiquement, il écoute des consignes en MQTT ou dans une table postgreSQL, traite les états souhaités du système par rapport à une configuration pré-établie, et envoie les ordres d'activation via MQTT.

Pour en savoir plus sur le projet ELFE - *Expérimentons Localement la Flexibilité Energétique*, consulter : https://www.projet-elfe.fr

## Documentation
Ce code est prévu pour fonctionner en articulation avec les autres composants informatiques du projet ELFE (à retrouver dans leurs dépôts dédiés).
L'utilisation de ce code est détaillée dans le ficher "documentation.pdf" présent dans le dépot.

## Auteurs et Licence
* Ce code a été écrit par **Stéphane Godin - Astrolabe CAE**. 
* Il appartient à l'association **Energies Citoyennes en Pays de Vilaine** - contact@enr-citoyennes.fr
* Dans un but d'essaimage et de construction coopérative, il est partagé sous licence EUPL v1.2
