
/*

apt install postgresql
cp -a /etc/postgresql/11/main/pg_hba.conf /etc/postgresql/11/main/pg_hba.conf.bak
sed -i "s/local   all             all                                     peer/local   all             all                                     scram-sha-256/g" /etc/postgresql/11/main/pg_hba.conf
service postgresql stop
service postgresql start

export PGSQL_DB_NAME=bdd_coordination
export PGSQL_USERNAME=coordination
export PGSQL_USERPWD="ebe16mMk5dQP"

cd /
/bin/su postgres --command "/usr/bin/createuser --no-superuser --no-createdb --no-createrole --login ${PGSQL_USERNAME}"
/bin/su postgres --command "/usr/bin/psql --command=\"ALTER USER ${PGSQL_USERNAME} PASSWORD '${PGSQL_USERPWD}'\""
/bin/su postgres --command "/usr/bin/createdb --encoding UTF8 --owner ${PGSQL_USERNAME} ${PGSQL_DB_NAME}"
/bin/su postgres --command "/usr/bin/psql --command \"GRANT ALL PRIVILEGES ON DATABASE ${PGSQL_DB_NAME} to ${PGSQL_USERNAME}\""


dump :
pg_dump  --username=${PGSQL_USERNAME}  --password --dbname=${PGSQL_DB_NAME}

use :
/bin/su postgres --command "/usr/bin/psql --username=${PGSQL_USERNAME}  --password --dbname=${PGSQL_DB_NAME}"

*/

/* Suivi de version
24/06/26 : v7.2 - A DEPLOYER
+ raccourcicement des identifiants de contraintes

30/04/26 : v7.1
+ ajout table des seuils pour l'API météo Cofy

10/02/26 : v7.0
+ ajout tables utilisateurs et cohortes
+ lien table utilisateurs vers equipement_domotique et equipement_pilote_ou_mesure
+ ajout Sommaire
+ retrait du epom chauffage asservi et des tables liées
+ evolution du materiel : ajout xky, suppr. capteur temp et doigt-robot
+ utiliser des heures creuses générales à l'échelle du foyer, au format YAML Home Assistant
+ généraliser les heures de confort du chauffage (voir exemple de home assistant)

02/06/23 : v6.3
+ ajout ligne 811 dans la table equipement_domotique_type
+ ajout table equipement_domotique_socorel_automate_v0

22/05/23 : v6.2
+ ajout ligne 190 dans equipement_pilote_typologie_installation_domotique

07/03/23 : v6.1
+ ajout champs dans la table equipement_pilote_ou_mesure : utilisateur, timestamp_de_derniere_programmation
+ pdl en format text (pour ne pas perdre le 0 initial)
+ suppression table "typologie vs. equipement domotique"
*/


/* TODO :
+ créer une vue multitables avec plein de colonnes, y compris équipement piloté, pour que les installateurs puissent rentrer les infos facilement
+ Passer tous les ID en texte pour faciliter configuration => Ou modifier le remplissage en récupérant l'id.
+ utiliser la clause "returning" pour remplir les foyers avec les id_serial
+ A étudier : rattacher l'écran au foyer et pas à l'équipement piloté
*/

/* Sommaire
#1 Enumerations (listes de valeurs statiques, codes d'état...)
#2 Tables des équipements pilotés
#3 Tables des équipements domotiques
*/

/* à réactiver après les tests

*/
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET client_min_messages = warning;
CREATE SCHEMA bdd_coordination_schema;
SET search_path TO bdd_coordination_schema, public;

-- #################### Partie 1 - Énumerations
--

--
-- Enumération : equipement_pilote_ou_mesure_type
--
CREATE TABLE equipement_pilote_ou_mesure_type (
  id integer NOT NULL CHECK (id > 0), /* ID de la ligne */
  nom text NOT NULL, /* Nom du type */
  nom_humain text NOT NULL, /* Nom de l'équipement piloté (à des fins d'IHM) */
  description text NOT NULL /* Description de l'équipement piloté (à des fins d'IHM) */
);
ALTER TABLE ONLY equipement_pilote_ou_mesure_type ADD CONSTRAINT equipement_pom_type_id_pkey PRIMARY KEY (id);

-- <400 : particulier
INSERT INTO equipement_pilote_ou_mesure_type (id, nom, nom_humain, description) VALUES (001, 'machine_generique',            'machine générique',     'Machine générique pouvant être pilotée par l''EMS (Energy Managment System) en déclenchement.');
INSERT INTO equipement_pilote_ou_mesure_type (id, nom, nom_humain, description) VALUES (111, 'lave_vaisselle',               'lave vaisselle',        'Lave vaisselle pouvant être pilotée par l''EMS (Energy Managment System) en déclenchement.');
INSERT INTO equipement_pilote_ou_mesure_type (id, nom, nom_humain, description) VALUES (112, 'lave_linge',                   'lave linge',            'Lave linge pouvant être piloté par l''EMS (Energy Managment System) en déclenchement.');
INSERT INTO equipement_pilote_ou_mesure_type (id, nom, nom_humain, description) VALUES (113, 'seche_linge',                  'sèche linge',           'Sèche linge pouvant être piloté par l''EMS (Energy Managment System) en déclenchement.');
INSERT INTO equipement_pilote_ou_mesure_type (id, nom, nom_humain, description) VALUES (131, 'ballon_ecs',                   'ballon d''eau chaude sanitaire électrique', 'Ballon d''eau chaude sanitaire électrique pouvant être piloté par l''EMS (Energy Managment System) en tout ou rien.');
INSERT INTO equipement_pilote_ou_mesure_type (id, nom, nom_humain, description) VALUES (151, 'chauffage_non_asservi',        'chauffage non asservi', 'Chauffage non asservi en température, pouvant être piloté par l''EMS (Energy Managment System) en éco/confort.');
INSERT INTO equipement_pilote_ou_mesure_type (id, nom, nom_humain, description) VALUES (155, 'chauffage_asservi',            'chauffage asservi',     'Chauffage asservi en température par l''EMS, pouvant être piloté en tout ou rien.');
INSERT INTO equipement_pilote_ou_mesure_type (id, nom, nom_humain, description) VALUES (221, 'voiture_electrique',           'voiture électrique',    'Voiture électrique, dont la recharge peut être pilotée par l''EMS.');
INSERT INTO equipement_pilote_ou_mesure_type (id, nom, nom_humain, description) VALUES (225, 'velo_assistance_electrique',   'vélo électrique',       'Vélo électrique, dont la recharge peut être pilotée par l''EMS.');
-- 400>499 : usage commun
INSERT INTO equipement_pilote_ou_mesure_type (id, nom, nom_humain, description) VALUES (410, 'compteur_electrique',          'compteur électrique',   'Compteur électrique donnant au moins la puissance instantanée');
-- > 500 : usage pro
INSERT INTO equipement_pilote_ou_mesure_type (id, nom, nom_humain, description) VALUES (515, 'chariot_elevateur_electrique', 'chariot élévateur',     'Chariot élévateur électrique, dont la recharge peut être pilotée par l''EMS.');
-- > 900 : production
INSERT INTO equipement_pilote_ou_mesure_type (id, nom, nom_humain, description) VALUES (901, 'centrale_elec_generique',      'centrale de production électrique générique', 'Centrale de production électrique générique, dont on mesure la production');
INSERT INTO equipement_pilote_ou_mesure_type (id, nom, nom_humain, description) VALUES (910, 'centrale_solaire_elec',        'centrale de production solaire',              'Centrale de production solaire, dont on mesure la production');
INSERT INTO equipement_pilote_ou_mesure_type (id, nom, nom_humain, description) VALUES (920, 'centrale_eolienne_elec',       'centrale de production éoliennne',            'Centrale de production éolienne, dont on mesure la production');


--
-- Enumération : equipement_pilote_ou_mesure_mode
--
CREATE TABLE equipement_pilote_ou_mesure_mode (
  id integer NOT NULL CHECK (id >= 0), /* ID de la ligne */
  nom text NOT NULL, /* Nom du mode */
  nom_humain text NOT NULL, /* Nom de l'équipement piloté (à des fins d'IHM) */
  description text NOT NULL /* Description de l'équipement piloté (à des fins d'IHM) */
);
ALTER TABLE ONLY equipement_pilote_ou_mesure_mode ADD CONSTRAINT equipement_pom_mode_id_pkey PRIMARY KEY (id);

INSERT INTO equipement_pilote_ou_mesure_mode (id, nom, nom_humain, description) VALUES (001, 'non_pilote',   'non piloté',            'Mode non pilotable : l''équipement n''est pas pilotable, typiquement dans le cas d''un équipement mesuré.');
INSERT INTO equipement_pilote_ou_mesure_mode (id, nom, nom_humain, description) VALUES (010, 'installation', 'installation en cours', 'Mode installation en cours : l''équipement n''est pas encore disponnible.');
INSERT INTO equipement_pilote_ou_mesure_mode (id, nom, nom_humain, description) VALUES (020, 'manuel',       'fonctionnement manuel', 'Mode manuel : l''utilisateur pilote directement l''équipement.');
INSERT INTO equipement_pilote_ou_mesure_mode (id, nom, nom_humain, description) VALUES (030, 'pilote',       'fonctionnement piloté', 'Mode piloté : l''EMS (Energy Managment System) pilote l''équipement.');
INSERT INTO equipement_pilote_ou_mesure_mode (id, nom, nom_humain, description) VALUES (070, 'desactive',    'désactivé',             'Mode désactivé : l''équipement est désactivé.');
INSERT INTO equipement_pilote_ou_mesure_mode (id, nom, nom_humain, description) VALUES (080, 'suppr',        'supprimé',              'Mode supprimé : l''équipement a été désinstallé.');


--
-- Enumération : equipement_pilote_etat_controle
--
CREATE TABLE equipement_pilote_etat_controle (
  id integer NOT NULL CHECK (id > 0), /* ID de la ligne */
  nom text NOT NULL, /* Nom de l'état de contrôle */
  nom_humain text NOT NULL, /* Nom de l'état de contrôle (à des fins d'IHM) */
  description text NOT NULL /* Description de l'état de contrôle (à des fins d'IHM) */
);
ALTER TABLE ONLY equipement_pilote_etat_controle ADD CONSTRAINT equipement_p_etat_controle_id_pkey PRIMARY KEY (id);

INSERT INTO equipement_pilote_etat_controle (id, nom, nom_humain, description) VALUES (015, 'on',      'marche',                  'L''équipement est alimenté. Il est en veille, en attente ou en fonctionnement.');
INSERT INTO equipement_pilote_etat_controle (id, nom, nom_humain, description) VALUES (025, 'off',     'arrêt',                   'L''équipement n''est pas alimenté. Il est à l''arrêt.');
INSERT INTO equipement_pilote_etat_controle (id, nom, nom_humain, description) VALUES (060, 'errcom',  'erreur de communication', 'Erreur de communication avec l''équipement.');
INSERT INTO equipement_pilote_etat_controle (id, nom, nom_humain, description) VALUES (070, 'inconnu', 'état inconnu',            'Etat inconnu.');


--
-- Enumération : equipement_pilote_etat_commande
-- Les différents états possibles dans l'ensemble des machines à état
--
CREATE TABLE equipement_pilote_etat_commande (
  id integer NOT NULL CHECK (id > 0), /* ID de la ligne */
  nom text NOT NULL, /* Nom de l'état de commande */
  nom_humain text NOT NULL, /* Nom de l'état de commande (à des fins d'IHM) */
  description text NOT NULL /* Description de l'état de commande (à des fins d'IHM) */
);
ALTER TABLE ONLY equipement_pilote_etat_commande ADD CONSTRAINT equipement_p_etat_commande_id_pkey PRIMARY KEY (id);

INSERT INTO equipement_pilote_etat_commande (id, nom, nom_humain, description) VALUES (001, 'etat_initial',             'état initial',            'Etat initial des appareils, au lancement du système ELFE.');
INSERT INTO equipement_pilote_etat_commande (id, nom, nom_humain, description) VALUES (011, 'pilote_stand_by',  'En attente de lancement', 'Consigne de pilotage reçue, appareil éteint en attente du créneau de lancement.');
INSERT INTO equipement_pilote_etat_commande (id, nom, nom_humain, description) VALUES (012, 'manuel_pilote_on',             'En marche controlée',            'Equipement allumé, en mode manuel ou piloté');
INSERT INTO equipement_pilote_etat_commande (id, nom, nom_humain, description) VALUES (013, 'manuel_on',             'En marche libre',  'Equi	pement allumé en mode manuel.');
INSERT INTO equipement_pilote_etat_commande (id, nom, nom_humain, description) VALUES (021, 'pilote_en_activation',  'En cours de lancement', 'Commande de lancement effectuée.');
INSERT INTO equipement_pilote_etat_commande (id, nom, nom_humain, description) VALUES (030, 'err',            'erreur',               'L''équipement est en erreur.');
INSERT INTO equipement_pilote_etat_commande (id, nom, nom_humain, description) VALUES (099, 'non_commande',            'Non-Commandé',               'L''équipement n''est pas commandé par ELFE.');


--
-- Enumération : equipement_pilote_typologie_installation_domotique
-- Les différents comportements/machines à état.
--
CREATE TABLE equipement_pilote_typologie_installation_domotique (
  id integer NOT NULL CHECK (id > 0), /* ID de la ligne */
  nom text NOT NULL, /* Nom de la typologie d'installation domotique */
  nom_humain text NOT NULL, /* Nom de la typologie d'installation domotique (à des fins d'IHM) */
  description text NOT NULL /* Description de de la typologie d'installation domotique (à des fins d'IHM) */
);
ALTER TABLE ONLY equipement_pilote_typologie_installation_domotique ADD CONSTRAINT equipement_p_typologie_install_domo_id_pkey PRIMARY KEY (id);

INSERT INTO equipement_pilote_typologie_installation_domotique (id, nom, nom_humain, description) VALUES (110, 'deux_relais',                 'Deux relais',                        'Un relai pour la mesure et un pour la commande.');
INSERT INTO equipement_pilote_typologie_installation_domotique (id, nom, nom_humain, description) VALUES (120, 'prise_commande',              'Une prise ou un relai commandé',     'Une prise ou relai qui mesure et commute le courant.');
INSERT INTO equipement_pilote_typologie_installation_domotique (id, nom, nom_humain, description) VALUES (130, 'prise_et_doigt',              'Une prise et un doigt',              'Une prise qui mesure et un doigt qui active.');
INSERT INTO equipement_pilote_typologie_installation_domotique (id, nom, nom_humain, description) VALUES (140, 'relai_et_capteur_temperature','Un relai et un capteur',             'Un relai qui mesure et commute, et un capteur d ambiance.');
INSERT INTO equipement_pilote_typologie_installation_domotique (id, nom, nom_humain, description) VALUES (150, 'prise_et_deux_doigts',        'Une prise et deux doigts',           'Une prise qui mesure, un doigt qui allume et un second qui active.');
INSERT INTO equipement_pilote_typologie_installation_domotique (id, nom, nom_humain, description) VALUES (160, 'prise_et_doigt_double_appui', 'Une prise et un doigt double-appui', 'Une prise qui mesure et un doigt qui fait deux pressions pour activer.');
INSERT INTO equipement_pilote_typologie_installation_domotique (id, nom, nom_humain, description) VALUES (170, 'prise_rallume_et_doigt',      'Une prise commandée et un doigt',    'Une prise qui mesure et commute, et un doigt qui active.');
INSERT INTO equipement_pilote_typologie_installation_domotique (id, nom, nom_humain, description) VALUES (180, 'relai_et_compteur',           'Un relai et un compteur général',    'Un relai qui commute uniquement, et un compteur général qui contient l''équipement activé.');
INSERT INTO equipement_pilote_typologie_installation_domotique (id, nom, nom_humain, description) VALUES (190, 'relai_inverse',           'Relai inversé',    'Un relai qui commute en inversé : équipement allumé quand le relai est OFF.');
INSERT INTO equipement_pilote_typologie_installation_domotique (id, nom, nom_humain, description) VALUES (200, 'TIC',           'Une carte de relève TIC',    'Une dispositif de lecture uniquement.');


--
-- Enumération : equipement_domotique_type
--
CREATE TABLE equipement_domotique_type (
  id integer NOT NULL CHECK (id > 0), /* ID de la ligne */
  nom text NOT NULL, /* Nom de l'équipement domotique */
  nom_humain text NOT NULL, /* Nom de l'équipement domotique (à des fins d'IHM) */
  description text NOT NULL /* Description de l'équipement domotique (à des fins d'IHM) */
);
ALTER TABLE ONLY equipement_domotique_type ADD CONSTRAINT equipement_domo_type_id_pkey PRIMARY KEY (id);

INSERT INTO equipement_domotique_type (id, nom, nom_humain, description) VALUES (111, 'shellyplugs_shellycloud_v1',   'Prise gigogne',          'Une prise électrique gigogne, branchée entre l''appareil et le secteur.');
INSERT INTO equipement_domotique_type (id, nom, nom_humain, description) VALUES (112, 'nous_a1t_tasmota_v12',         'Prise gigogne',          'Une prise électrique gigogne, branchée entre l''appareil et le secteur.');
INSERT INTO equipement_domotique_type (id, nom, nom_humain, description) VALUES (211, 'teleinfo_tasmota_v12',         'Carte téléinfo',         'Une carte électronique qui relève les informations émises par le compteur électrique.');
INSERT INTO equipement_domotique_type (id, nom, nom_humain, description) VALUES (212, 'xky_tasmota_v12',         'Module xKy Wifi',         'Une carte électronique sans fil qui relève les informations émises par le compteur électrique.');
INSERT INTO equipement_domotique_type (id, nom, nom_humain, description) VALUES (311, 'switchbot_mqtt2ble_v7',        'Doigt robot',            'Un doigt mécanique alimenté par une pile, et sa carte-passerelle wifi.');
INSERT INTO equipement_domotique_type (id, nom, nom_humain, description) VALUES (411, 'shellyplus1pm_shellycloud_v1', 'Relai connecté',         'Un relai commandé, installé dans le circuit électrique du participant.');
INSERT INTO equipement_domotique_type (id, nom, nom_humain, description) VALUES (611, 'shellyht_shellycloud_v1',      'Capteur de température', 'Un capteur de température et d’humidité ambiantes, alimenté par une pile.');
INSERT INTO equipement_domotique_type (id, nom, nom_humain, description) VALUES (711, 'm5stackcore2_openhasp_v0',     'Ecran tactile',          'Un écran tactile compact avec batterie, rechargeable par port USB C.');
INSERT INTO equipement_domotique_type (id, nom, nom_humain, description) VALUES (811, 'socorel_automate_v0',     'Automate Socorel',          'Un canal entrée-sortie sur un automate programmable');


--
-- Enumération : equipement_domotique_usage
--
CREATE TABLE equipement_domotique_usage (
  id integer NOT NULL CHECK (id > 0), /* ID de la ligne */
  nom text NOT NULL, /* Nom de l'usage de l'équipement domotique */
  nom_humain text NOT NULL, /* Nom de l'usage de l'équipement domotique (à des fins d'IHM) */
  description text NOT NULL /* Description de l'usage de l'équipement domotique (à des fins d'IHM) */
);
ALTER TABLE ONLY equipement_domotique_usage ADD CONSTRAINT equipement_domo_usage_id_pkey PRIMARY KEY (id);

INSERT INTO equipement_domotique_usage (id, nom, nom_humain, description) VALUES (11, 'mesurer_elec_commuter',  'Mesurer et commuter',   'Mesure un circuit électrique et le commute');
INSERT INTO equipement_domotique_usage (id, nom, nom_humain, description) VALUES (12, 'commuter',               'Commuter',              'Commute un circuit électrique');
INSERT INTO equipement_domotique_usage (id, nom, nom_humain, description) VALUES (21, 'mesurer_elec',           'Mesurer électrique',    'Mesure un circuit électrique');
INSERT INTO equipement_domotique_usage (id, nom, nom_humain, description) VALUES (31, 'appuyer_power',          'Appui sur Power',       'Appuie sur le bouton de mise sous tension d''un équipement');
INSERT INTO equipement_domotique_usage (id, nom, nom_humain, description) VALUES (32, 'appuyer_demarrage',      'Appui sur Démarrage',   'Appuie sur le bouton de démarrage d un équipement');
INSERT INTO equipement_domotique_usage (id, nom, nom_humain, description) VALUES (61, 'mesurer_ambiance',       'Mesurer ambiance',      'Mesure la température et l''humidité d''un lieu');
INSERT INTO equipement_domotique_usage (id, nom, nom_humain, description) VALUES (71, 'ihm',                    'Interface utilisateur', 'Affiche des informations et reçoit des consignes de l''utilisateur');

-- #################### Partie 1bis - Utilisateurs cohortes et meteos
--

-- Enumération : cohortes_utilisateurs
--
CREATE TABLE cohorte_utilisateurs (
  id text NOT NULL, /* Identifiant de la cohorte */
  nom text NOT NULL, /* Nom de la cohorte (à des fins d'IHM)*/
  description text NOT NULL, /* Description de l'usage de l'équipement domotique (à des fins d'IHM) */
  prevision_ID text NOT NULL /* Identifiant du signal de prevision énergétique associé à la cohorte */
);
ALTER TABLE ONLY cohorte_utilisateurs ADD CONSTRAINT cohortes_utilisateurs_id_pkey PRIMARY KEY (id);

INSERT INTO cohorte_utilisateurs (id, nom, description, prevision_ID) VALUES ('ACC_1',  	'AutoConsoCollective Boucle 1',   	'Boucle ACC citoyenne de Saint Perreux', 	'prev_ACC_1');
INSERT INTO cohorte_utilisateurs (id, nom, description, prevision_ID) VALUES ('ACC_2',  	'AutoConsoCollective Boucle 2',   	'Boucle ACC de Pipriac',					'prev_ACC_2');
INSERT INTO cohorte_utilisateurs (id, nom, description, prevision_ID) VALUES ('ML_1',  		'Marché Local 1',  					'Marché Local Pays de Vilaine',				'prev_ML_1');
INSERT INTO cohorte_utilisateurs (id, nom, description, prevision_ID) VALUES ('ACI_1',  	'AutoConsoIndividuelle 1',   		'Groupe autoconsomateurs individuels', 		'prev_ACI_1');
INSERT INTO cohorte_utilisateurs (id, nom, description, prevision_ID) VALUES ('TD_1',  		'Tarif dynamique 1',   				'Clients Enercoop FlexiWatt toutes options', 'prev_TD_1');
INSERT INTO cohorte_utilisateurs (id, nom, description, prevision_ID) VALUES ('TD_2',  		'Tarif dynamique 1',   				'Clients autres fournisseurs',				'prev_TD_2');
INSERT INTO cohorte_utilisateurs (id, nom, description, prevision_ID) VALUES ('BetaTest',	'BetaTest',   						'Groupe des betatesteurs', 					'prev_BetaTest');



-- Structure de table : seuils_api_meteo
--
CREATE TABLE seuils_api_meteo (
  id text NOT NULL, /* Identifiant de la cohorte */
  timestamp_debut_validite int NOT NULL, /* timestamp à partir duquel les seuils doivent être pris en compte par l'API */
  seuil_neg2 float NOT NULL, /* seuil inférieur, entre signal '--' et '-' */
  seuil_neg1 float NOT NULL, /* seuil intermédiaire inférieur, entre signal '-' et '0' */
  seuil_pos1 float NOT NULL, /* seuil intermédiaire supérieur, entre signal '0' et '+' */
  seuil_pos2 float NOT NULL  /* seuil supérieur, entre signal '+' et '++'*/
);
ALTER TABLE ONLY seuils_api_meteo ADD CONSTRAINT seuils_api_meteo_pkey PRIMARY KEY (id,timestamp_debut_validite);
ALTER TABLE ONLY seuils_api_meteo ADD CONSTRAINT seuils_api_meteo_fkey FOREIGN KEY (id) REFERENCES cohorte_utilisateurs(id) ON UPDATE CASCADE ON DELETE RESTRICT;

INSERT INTO seuils_api_meteo VALUES ('ACC_1',  	'178000000',   	'-1000000.1', '-1000000','1000000','1000000.1');


--
-- Structure de table pour la table utilisateur
--
CREATE TABLE utilisateur (
  id text NOT NULL, /* Identifiant Projet de l'utilisateur */
  cohorte text NOT NULL /* Cohorte d'appartenance */
);
ALTER TABLE ONLY utilisateur ADD CONSTRAINT utilisateur_id_pkey PRIMARY KEY (id);
ALTER TABLE ONLY utilisateur ADD CONSTRAINT utilisateur_cohorte_fkey FOREIGN KEY (cohorte) REFERENCES cohorte_utilisateurs(id) ON UPDATE CASCADE ON DELETE RESTRICT;


-- Structure de table pour la table heures_creuses_utilisateur
--
CREATE TABLE heures_creuses_utilisateur (
  id serial NOT NULL, /* ID de la ligne */
  utilisateur_id text NOT NULL, /* ID de equipement_pilote_ballon_ecs */
  jour text NOT NULL, /* jour de la semaine en anglais minuscule */
  periode text NOT NULL /* Periodes concaténées au format YAML de Home Assistant : "- from '12:00:00' to '14:30:00' -from '22:00:00' to '23:59:59' */
);
ALTER TABLE ONLY heures_creuses_utilisateur ADD CONSTRAINT heures_creuses_utilisateurs_id_pkey PRIMARY KEY (id);
ALTER TABLE ONLY heures_creuses_utilisateur ADD CONSTRAINT heures_creuses_utilisateurs_fkey FOREIGN KEY (utilisateur_id) REFERENCES utilisateur(id) ON UPDATE CASCADE ON DELETE RESTRICT;
ALTER TABLE ONLY heures_creuses_utilisateur ADD CONSTRAINT heures_creuses_utilisateurs_unicite UNIQUE (utilisateur_id, jour);

-- #################### Partie 2 - Tables des equipements pilotés
--

-- Structure de table pour la table equipement_pilote
--
CREATE TABLE equipement_pilote_ou_mesure (
  id serial NOT NULL, /* ID de la ligne */
  equipement_pilote_specifique_id integer NOT NULL, /* ID de l'équipement piloté dans sa table spécifique (polymorphisme) */
  typologie_installation_domotique_id integer NOT NULL CHECK (typologie_installation_domotique_id > 0), /* ID dans la table : equipement_pilote_typologie_installation_domotique, guide l'algorithme de contrôle des équipements domotiques pour choisir la machine à état à utiliser */
  nom_humain text NOT NULL, /* Nom spécifique de l'équipement piloté (à des fins d'IHM) - mettre au nom_humain de la table equipement_pilote_ou_mesure_type si il n'y en a pas */
  description text NOT NULL, /* Description de l'équipement piloté - (mettre à "aucun" si il n'y en a pas) */
  equipement_pilote_ou_mesure_type_id integer NOT NULL CHECK (equipement_pilote_ou_mesure_type_id > 0), /* ID dans la table : equipement_pilote_ou_mesure_type */
  equipement_pilote_ou_mesure_mode_id integer NOT NULL CHECK (equipement_pilote_ou_mesure_mode_id > 0), /* ID dans la table : equipement_pilote_ou_mesure_mode. Si c'est un équipement uniquement mesuré, on met 001 : 'non_pilote' */
  etat_controle_id integer NOT NULL CHECK (etat_controle_id > 0), /* ID dans dans la table : equipement_pilote_etat_controle. Si c'est un équipement mesuré, on met 015 : 'on'. Sert à savoir l'état 'réel' d'un équipement piloté. */
  etat_commande_id integer NOT NULL CHECK (etat_commande_id > 0), /* ID dans dans la table : equipement_pilote_etat_commande. Si c'est un équipement mesuré, on met 015 : 'on'. Sert pour l'enregistrement de l'état en cours dans la machine à états correspondante. */
  ems_consigne_marche boolean NOT NULL, /* Consigne courante de l'Energy Managment System */
  timestamp_derniere_mise_en_marche integer default 0 NOT NULL CHECK (timestamp_derniere_mise_en_marche >= 0), /* secondes depuis le 1 er janvier 1970 00:00:00 UTC */
  timestamp_derniere_programmation integer default 0 NOT NULL CHECK (timestamp_derniere_programmation >= 0), /* secondes depuis le 1 er janvier 1970 00:00:00 UTC */
  utilisateur text NOT NULL /* utilisateur de l'équipement piloté */
);
ALTER TABLE ONLY equipement_pilote_ou_mesure ADD CONSTRAINT equipement_pom_id_pkey PRIMARY KEY (id);
ALTER TABLE ONLY equipement_pilote_ou_mesure ADD CONSTRAINT equipement_pom_type_id_fkey FOREIGN KEY (equipement_pilote_ou_mesure_type_id) REFERENCES equipement_pilote_ou_mesure_type(id) ON UPDATE CASCADE ON DELETE RESTRICT;
ALTER TABLE ONLY equipement_pilote_ou_mesure ADD CONSTRAINT equipement_pom_mode_id_fkey FOREIGN KEY (equipement_pilote_ou_mesure_mode_id) REFERENCES equipement_pilote_ou_mesure_mode(id) ON UPDATE CASCADE ON DELETE RESTRICT;
ALTER TABLE ONLY equipement_pilote_ou_mesure ADD CONSTRAINT etat_controle_id_fkey FOREIGN KEY (etat_controle_id) REFERENCES equipement_pilote_etat_controle(id) ON UPDATE CASCADE ON DELETE RESTRICT;
ALTER TABLE ONLY equipement_pilote_ou_mesure ADD CONSTRAINT etat_commande_id_fkey FOREIGN KEY (etat_commande_id) REFERENCES equipement_pilote_etat_commande(id) ON UPDATE CASCADE ON DELETE RESTRICT;
ALTER TABLE ONLY equipement_pilote_ou_mesure ADD CONSTRAINT typologie_install_domo_id_fkey FOREIGN KEY (typologie_installation_domotique_id) REFERENCES equipement_pilote_typologie_installation_domotique(id) ON UPDATE CASCADE ON DELETE RESTRICT;
ALTER TABLE ONLY equipement_pilote_ou_mesure ADD CONSTRAINT utilisateur_fkey FOREIGN KEY (utilisateur) REFERENCES utilisateur(id) ON UPDATE CASCADE ON DELETE RESTRICT;
ALTER TABLE ONLY equipement_pilote_ou_mesure ADD CONSTRAINT equipement_p_polymorphism_uniq UNIQUE (id, equipement_pilote_specifique_id);


--
-- Structure de table pour la table equipement_pilote_machine_generique
--
CREATE TABLE equipement_pilote_machine_generique (
  id serial NOT NULL, /* ID de la ligne */
  equipement_pilote_ou_mesure_id integer NOT NULL, /* ID de equipement_pilote_ou_mesure */
  timestamp_de_fin_souhaite integer NOT NULL CHECK (timestamp_de_fin_souhaite >= 0), /* secondes depuis le 1 er janvier 1970 00:00:00 UTC */
  delai_attente_maximale_apres_fin integer NOT NULL CHECK (delai_attente_maximale_apres_fin >= 0), /* delta en secondes */
  mesures_puissance_elec_id integer NOT NULL CHECK (mesures_puissance_elec_id > 0) /* ID d'élément dans la table des mesures - Zabbix element ID */
);
ALTER TABLE ONLY equipement_pilote_machine_generique ADD CONSTRAINT equipement_p_machine_generique_id_pkey PRIMARY KEY (id);
ALTER TABLE ONLY equipement_pilote_machine_generique ADD CONSTRAINT equipement_p_machine_generique_equipement_pom_id_fkey FOREIGN KEY (equipement_pilote_ou_mesure_id) REFERENCES equipement_pilote_ou_mesure(id) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Structure de table pour la table equipement_pilote_vehicule_electrique_generique
--
CREATE TABLE equipement_pilote_vehicule_electrique_generique (
  id serial NOT NULL, /* ID de la ligne */
  equipement_pilote_ou_mesure_id integer NOT NULL, /* ID de equipement_pilote_ou_mesure */
  pourcentage_charge_restant integer NOT NULL CHECK (pourcentage_charge_restant >= 0), /* pourcentage */
  pourcentage_charge_finale_minimale_souhaitee integer NOT NULL CHECK (pourcentage_charge_finale_minimale_souhaitee > 0), /* pourcentage */
  duree_de_charge_estimee integer NOT NULL CHECK (duree_de_charge_estimee >= 0), /* secondes */
  timestamp_dispo_souhaitee integer NOT NULL CHECK (timestamp_dispo_souhaitee >= 0), /* secondes depuis le 1 er janvier 1970 00:00:00 UTC */
  puissance_de_charge integer NOT NULL CHECK (puissance_de_charge > 0),  /* W */
  capacite_de_batterie integer NOT NULL CHECK (capacite_de_batterie > 0),  /* Wh */
  mesures_puissance_elec_id integer NOT NULL CHECK (mesures_puissance_elec_id > 0) /* ID d'élément dans la table des mesures - Zabbix element ID */
);
ALTER TABLE ONLY equipement_pilote_vehicule_electrique_generique ADD CONSTRAINT equipement_p_vehicule_electrique_generique_id_pkey PRIMARY KEY (id);
ALTER TABLE ONLY equipement_pilote_vehicule_electrique_generique ADD CONSTRAINT equipement_p_vehicule_electrique_generique_equipement_pom_id_fkey FOREIGN KEY (equipement_pilote_ou_mesure_id) REFERENCES equipement_pilote_ou_mesure(id) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Structure de table pour la table equipement_pilote_ballon_ecs
--
CREATE TABLE equipement_pilote_ballon_ecs (
  id serial NOT NULL, /* ID de la ligne */
  equipement_pilote_ou_mesure_id integer NOT NULL, /* ID de equipement_pilote_ou_mesure */
  volume_ballon integer NOT NULL CHECK (volume_ballon > 0), /* litre */
  puissance_chauffe integer NOT NULL CHECK (puissance_chauffe > 0), /* W */
  /* horaire_utilisation_eau_chaude_1 integer NOT NULL CHECK (horaire_utilisation_eau_chaude_1 > 0), nombre de secondes écoulé dans 1 journée depuis 0h00 UTC */
  /* horaire_utilisation_eau_chaude_2 integer NOT NULL CHECK (horaire_utilisation_eau_chaude_2 > 0),  nombre de secondes écoulé dans 1 journée depuis 0h00 UTC */
  mesures_puissance_elec_id integer NOT NULL CHECK (mesures_puissance_elec_id > 0) /* ID d'élément dans la table des mesures - Zabbix element ID */
);
ALTER TABLE ONLY equipement_pilote_ballon_ecs ADD CONSTRAINT equipement_p_ballon_ecs_id_pkey PRIMARY KEY (id);
ALTER TABLE ONLY equipement_pilote_ballon_ecs ADD CONSTRAINT equipement_p_ballon_ecs_equipement_pom_id_fkey FOREIGN KEY (equipement_pilote_ou_mesure_id) REFERENCES equipement_pilote_ou_mesure(id) ON UPDATE CASCADE ON DELETE RESTRICT;



--
-- Structure de table pour la table  equipement_pilote_chauffage_non_asservi
-- chauffage en mode programmation + délestage
--
CREATE TABLE equipement_pilote_chauffage_non_asservi (
  id serial NOT NULL, /* ID de la ligne */
  equipement_pilote_ou_mesure_id integer NOT NULL, /* ID de equipement_pilote_ou_mesure */
  prog_semaine_periode_1_confort_actif boolean NOT NULL, /* booléen */
  prog_semaine_periode_1_confort_heure_debut integer NOT NULL CHECK (prog_semaine_periode_1_confort_heure_debut > 0), /* nombre de secondes écoulées dans 1 journée depuis 0h00*/
  prog_semaine_periode_1_confort_heure_fin integer NOT NULL CHECK (prog_semaine_periode_1_confort_heure_fin > 0), /* nombre de secondes écoulées dans 1 journée depuis 0h00*/
  prog_semaine_periode_2_confort_actif boolean NOT NULL, /* booléen */
  prog_semaine_periode_2_confort_heure_debut integer NOT NULL CHECK (prog_semaine_periode_2_confort_heure_debut > 0), /* nombre de secondes écoulées dans 1 journée depuis 00h00*/
  prog_semaine_periode_2_confort_heure_fin integer NOT NULL CHECK (prog_semaine_periode_2_confort_heure_fin > 0), /* nombre de secondes écoulées dans 1 journée depuis 00h00*/
  prog_weekend_periode_1_confort_actif boolean NOT NULL, /* booléen */
  prog_weekend_periode_1_confort_heure_debut integer NOT NULL CHECK (prog_weekend_periode_1_confort_heure_debut > 0), /* nombre de secondes écoulées dans 1 journée depuis 0h00*/
  prog_weekend_periode_1_confort_heure_fin integer NOT NULL CHECK (prog_weekend_periode_1_confort_heure_fin > 0), /* nombre de secondes écoulées dans 1 journée depuis 0h00*/
  prog_weekend_periode_2_confort_actif boolean NOT NULL, /* booléen */
  prog_weekend_periode_2_confort_heure_debut integer NOT NULL CHECK (prog_weekend_periode_2_confort_heure_debut > 0), /* nombre de secondes écoulées dans 1 journée depuis 0h00*/
  prog_weekend_periode_2_confort_heure_fin integer NOT NULL CHECK (prog_weekend_periode_2_confort_heure_fin > 0), /* nombre de secondes écoulées dans 1 journée depuis 0h00*/
  puissance_moyenne_eco integer NOT NULL CHECK (puissance_moyenne_eco > 0),  /* W */
  puissance_moyenne_confort integer NOT NULL CHECK (puissance_moyenne_confort > 0),  /* W */
  pourcentage_eco_force integer NOT NULL CHECK (pourcentage_eco_force > 0), /* pourcentage du temps ou on force en éco alors que l'on devrait être en confort */
  mesures_puissance_elec_id integer NOT NULL CHECK (mesures_puissance_elec_id > 0) /* ID d'élément dans la table des mesures - Zabbix element ID */
);
ALTER TABLE ONLY equipement_pilote_chauffage_non_asservi ADD CONSTRAINT equipement_p_chauffage_non_asservi_id_pkey PRIMARY KEY (id);
ALTER TABLE ONLY equipement_pilote_chauffage_non_asservi ADD CONSTRAINT equipement_p_chauffage_non_asservi_equipement_pom_id_fk FOREIGN KEY (equipement_pilote_ou_mesure_id) REFERENCES equipement_pilote_ou_mesure(id) ON UPDATE CASCADE ON DELETE RESTRICT;

--
-- Structure de table pour la table chauffage_planning_de_confort
--
CREATE TABLE chauffage_planning_de_confort (
  id serial NOT NULL, /* ID de la ligne */
  equipement_pilote_chauffage_non_asservi_id integer NOT NULL, /* ID de equipement_pilote_chauffage_non_asservi */
  jour text NOT NULL, /* jour de la semaine en anglais minuscule */
  periode text NOT NULL /* Periodes concaténées au format YAML de Home Assistant : "- from '12:00:00' to '14:30:00' -from '22:00:00' to '23:59:59' */
);
ALTER TABLE ONLY chauffage_planning_de_confort ADD CONSTRAINT chauffage_planning_de_confortid_pkey PRIMARY KEY (id);
ALTER TABLE ONLY chauffage_planning_de_confort ADD CONSTRAINT chauffage_planning_de_confort_chauffage_fkey FOREIGN KEY (equipement_pilote_chauffage_non_asservi_id) REFERENCES equipement_pilote_chauffage_non_asservi(id) ON UPDATE CASCADE ON DELETE RESTRICT;
ALTER TABLE ONLY chauffage_planning_de_confort ADD CONSTRAINT chauffage_planning_de_confort_unicite UNIQUE (equipement_pilote_chauffage_non_asservi_id, jour);


--
-- Structure de table pour la table equipement_mesure_compteur_electrique
--
CREATE TABLE equipement_mesure_compteur_electrique (
  id serial NOT NULL, /* ID de la ligne */
  equipement_pilote_ou_mesure_id integer NOT NULL, /* ID de equipement_pilote_ou_mesure */
  numero_pdl text NOT NULL, /* numéro du point de livraison du compteur, référence externe, valeur par défaut : 0 */
  mesures_puissance_elec_id integer NOT NULL CHECK (mesures_puissance_elec_id > 0) /* ID d'élément dans la table des mesures - Zabbix element ID */
);
ALTER TABLE ONLY equipement_mesure_compteur_electrique ADD CONSTRAINT equipement_mesure_compteur_electrique_id_pkey PRIMARY KEY (id);
ALTER TABLE ONLY equipement_mesure_compteur_electrique ADD CONSTRAINT equipement_mesure_compteur_electrique_equipement_pom_id_fkey FOREIGN KEY (equipement_pilote_ou_mesure_id) REFERENCES equipement_pilote_ou_mesure(id) ON UPDATE CASCADE ON DELETE RESTRICT;


CREATE TABLE equipement_mesure_centrale_elec_generique (
  id serial NOT NULL, /* ID de la ligne */
  equipement_pilote_ou_mesure_id integer NOT NULL, /* ID de equipement_pilote_ou_mesure */
  mesures_puissance_elec_id integer NOT NULL CHECK (mesures_puissance_elec_id > 0), /* ID d'élément dans la table des mesures - Zabbix element ID */
  puissance_installee integer, /* Puissance installée en VA ou Wc */
  orientation integer /* Orientation des panneaux en Azimuth, 0 = Nord, 90 = Est */
);
ALTER TABLE ONLY equipement_mesure_centrale_elec_generique ADD CONSTRAINT equipement_mesure_centrale_elec_generique_id_pkey PRIMARY KEY (id);
ALTER TABLE ONLY equipement_mesure_centrale_elec_generique ADD CONSTRAINT equipement_mesure_centrale_elec_generique_equipement_pom_id_fkey FOREIGN KEY (equipement_pilote_ou_mesure_id) REFERENCES equipement_pilote_ou_mesure(id) ON UPDATE CASCADE ON DELETE RESTRICT;



-- #################### Partie 3 - Équipements domotiques
--


--
-- Structure de table pour la table equipement_domotique
--
CREATE TABLE equipement_domotique (
  id text NOT NULL, /* ID de la ligne, correspond à l'ID d'équipement ELFE, ex : D101 */
  equipement_pilote_ou_mesure_id integer NOT NULL, /* ID de equipement_pilote_ou_mesure */
  equipement_domotique_type_id integer NOT NULL CHECK (equipement_domotique_type_id > 0), /* ID dans la table equipement_domotique_type */
  equipement_domotique_usage_id integer NOT NULL CHECK (equipement_domotique_usage_id > 0), /* ID dans la table equipement_domotique_usage */
  id_materiel text default 'non renseigné', /* ID du matériel, par exemple son adresse MAC */
  marque text default 'non renseigné', /* marque du matériel */
  utilisateur text NOT NULL, /* utilisateur du matériel */
  utilisateur_affecte boolean NOT NULL, /* booléen signifiant qu'un utilisateur est affecté */
  equipement_domotique_specifique_id text NOT NULL /* ID de l'équipement domotique dans sa table spécifique (polymorphisme) */
);
ALTER TABLE ONLY equipement_domotique ADD CONSTRAINT equipement_domotique_id_pkey PRIMARY KEY (id);
ALTER TABLE ONLY equipement_domotique ADD CONSTRAINT equipement_domotique_equipement_pom_id_fkey FOREIGN KEY (equipement_pilote_ou_mesure_id) REFERENCES equipement_pilote_ou_mesure(id) ON UPDATE CASCADE ON DELETE RESTRICT;
ALTER TABLE ONLY equipement_domotique ADD CONSTRAINT equipement_domotique_type_id_fkey FOREIGN KEY (equipement_domotique_type_id) REFERENCES equipement_domotique_type(id) ON UPDATE CASCADE ON DELETE RESTRICT;
ALTER TABLE ONLY equipement_domotique ADD CONSTRAINT equipement_domotique_usage_id_fkey FOREIGN KEY (equipement_domotique_usage_id) REFERENCES equipement_domotique_usage(id) ON UPDATE CASCADE ON DELETE RESTRICT;
ALTER TABLE ONLY equipement_domotique ADD CONSTRAINT equipement_domotique_utilisateur_fkey FOREIGN KEY (utilisateur) REFERENCES utilisateur(id) ON UPDATE CASCADE ON DELETE RESTRICT;
ALTER TABLE ONLY equipement_domotique ADD CONSTRAINT equipement_domotique_polymorphism_uniq UNIQUE (id, equipement_domotique_specifique_id);


--
-- Structure de table pour la table equipement_domotique_shellyplugs_shellycloud_v1
--
CREATE TABLE equipement_domotique_shellyplugs_shellycloud_v1 (
  id text NOT NULL, /* ID de la ligne */
  equipement_domotique_id text NOT NULL, /* ID de equipement_domotique */
  topic_mqtt_controle_json text NOT NULL, /* topic MQTT qui donne un JSON contenant les états de controle */
  topic_mqtt_commande_text text NOT NULL, /* topic MQTT générique dans lequel on envoie une commande sous forme de texte */
  topic_mqtt_lwt text NOT NULL /* topic MQTT Last Will and Testament */
);
/*
contrôle : shellies/shellyplug-s-4375BD/relay/0
commande : shellies/shellyplug-s-4375BD/relay/0/command
LWT : shellies/shellyplug-s-4375BD/online
*/
ALTER TABLE ONLY equipement_domotique_shellyplugs_shellycloud_v1 ADD CONSTRAINT equipement_domo_shellyplugs_shellycloud_v1_id_pkey PRIMARY KEY (id);
ALTER TABLE ONLY equipement_domotique_shellyplugs_shellycloud_v1 ADD CONSTRAINT equipement_domo_shellyplugs_shellycloud_v1_equip_domo_id_fkey FOREIGN KEY (equipement_domotique_id) REFERENCES equipement_domotique(id) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Structure de table pour la table equipement_domotique_nous_a1t_tasmota_v12
--
CREATE TABLE equipement_domotique_nous_a1t_tasmota_v12 (
  id text NOT NULL, /* ID de la ligne */
  equipement_domotique_id text NOT NULL, /* ID de equipement_domotique */
  topic_mqtt_controle_json text NOT NULL, /* topic MQTT qui donne un JSON contenant les états de controle */
  topic_mqtt_commande_text text NOT NULL, /* topic MQTT générique dans lequel on envoie une commande sous forme de texte */
  topic_mqtt_lwt text NOT NULL /* topic MQTT Last Will and Testament */
);
/*
contrôle : tele/A110
commande : cmd/A110
LWT : tele/A115/LWT
*/
ALTER TABLE ONLY equipement_domotique_nous_a1t_tasmota_v12 ADD CONSTRAINT equipement_domo_nous_a1t_tasmota_v12_id_pkey PRIMARY KEY (id);
ALTER TABLE ONLY equipement_domotique_nous_a1t_tasmota_v12 ADD CONSTRAINT equipement_domo_nous_a1t_tasmota_v12_eq_dom_id_fkey FOREIGN KEY (equipement_domotique_id) REFERENCES equipement_domotique(id) ON UPDATE CASCADE ON DELETE RESTRICT;

--
-- Structure de table pour la table equipement_domotique_teleinfo_tasmota_v12
--
CREATE TABLE equipement_domotique_teleinfo_tasmota_v12 (
  id text NOT NULL, /* ID de la ligne */
  equipement_domotique_id text NOT NULL, /* ID de equipement_domotique */
  topic_mqtt_controle_json text NOT NULL, /* topic MQTT qui donne un JSON contenant les états de controle */
  topic_mqtt_commande_text text NOT NULL, /* topic MQTT générique dans lequel on envoie une commande sous forme de texte */
  topic_mqtt_lwt text NOT NULL /* topic MQTT Last Will and Testament */
);
/*
contrôle : tele/B008/SENSOR
commande : cmnd/B008/POWER
LWT : tele/B008/LWT
*/
ALTER TABLE ONLY equipement_domotique_teleinfo_tasmota_v12 ADD CONSTRAINT equipement_domo_teleinfo_tasmota_v12_id_pkey PRIMARY KEY (id);
ALTER TABLE ONLY equipement_domotique_teleinfo_tasmota_v12 ADD CONSTRAINT equipement_domo_teleinfo_tasmota_v12_eq_dom_id_fkey FOREIGN KEY (equipement_domotique_id) REFERENCES equipement_domotique(id) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Structure de table pour la table equipement_domotique_xky_tasmota_v12
--
CREATE TABLE equipement_domotique_xky_tasmota_v12 (
  id text NOT NULL, /* ID de la ligne */
  equipement_domotique_id text NOT NULL, /* ID de equipement_domotique */
  topic_mqtt_controle_json text NOT NULL, /* topic MQTT qui donne un JSON contenant les états de controle */
  topic_mqtt_commande_text text NOT NULL, /* topic MQTT générique dans lequel on envoie une commande sous forme de texte */
  topic_mqtt_lwt text NOT NULL /* topic MQTT Last Will and Testament */
);
/*
contrôle : tele/xky_001/SENSOR
commande : -
LWT : tele/xky/LWT
*/
ALTER TABLE ONLY equipement_domotique_xky_tasmota_v12 ADD CONSTRAINT equipement_domo_xky_tasmota_v12_id_pkey PRIMARY KEY (id);
ALTER TABLE ONLY equipement_domotique_xky_tasmota_v12 ADD CONSTRAINT equipement_domo_teleinfo_tasmota_v12_eq_dom_id_fkey FOREIGN KEY (equipement_domotique_id) REFERENCES equipement_domotique(id) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Structure de table pour la table equipement_domotique_shellyplus1pm_shellycloud_v1
--
CREATE TABLE equipement_domotique_shellyplus1pm_shellycloud_v1 (
  id text NOT NULL, /* ID de la ligne */
  equipement_domotique_id text NOT NULL, /* ID de equipement_domotique */
  topic_mqtt_controle_et_mesure_json text NOT NULL, /* topic MQTT qui donne un JSON contenant les états de controle et les mesures */
  topic_mqtt_commande_json text NOT NULL, /* topic MQTT générique dans lequel on envoie une commande sous forme de JSON */
  topic_mqtt_lwt text default 'aucun' /* topic MQTT Last Will and Testament */
);
/*
contrôle : D002/status/switch:0
commande : D002/events/rpc
LWT : D022/online
*/
ALTER TABLE ONLY equipement_domotique_shellyplus1pm_shellycloud_v1 ADD CONSTRAINT equipement_domo_shellyplus1pm_shellycloud_v1_id_pkey PRIMARY KEY (id);
ALTER TABLE ONLY equipement_domotique_shellyplus1pm_shellycloud_v1 ADD CONSTRAINT equipement_domo_shellyplus1pm_shellycloud_v1_eq_dom_id_fkey FOREIGN KEY (equipement_domotique_id) REFERENCES equipement_domotique(id) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Structure de table pour la table equipement_domotique_m5stackcore2_openhasp_v0
--
CREATE TABLE equipement_domotique_m5stackcore2_openhasp_v0 (
  id text NOT NULL, /* ID de la ligne */
  equipement_domotique_id text NOT NULL, /* ID de equipement_domotique */
  topic_mqtt_controle_json text NOT NULL, /* topic MQTT qui donne un JSON contenant les états de controle */
  topic_mqtt_commande_text text NOT NULL, /* topic MQTT générique dans lequel on envoie une commande sous forme de texte */
  topic_mqtt_lwt text NOT NULL /* topic MQTT Last Will and Testament */
);
/*
contrôle : hasp/g001/page
commande : hasp/g001/cmd/jsonl
LWT : hasp/g001/LWT
*/
ALTER TABLE ONLY equipement_domotique_m5stackcore2_openhasp_v0 ADD CONSTRAINT equipement_domo_m5stackcore2_openhasp_v0_id_pkey PRIMARY KEY (id);
ALTER TABLE ONLY equipement_domotique_m5stackcore2_openhasp_v0 ADD CONSTRAINT equipement_domo_m5stackcore2_openhasp_v0_eq_dom_id_fkey FOREIGN KEY (equipement_domotique_id) REFERENCES equipement_domotique(id) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Structure de table pour la table equipement_domotique_socorel_automate_v0
--
/*
Chaque automate physique dispose de plusieurs entrées/sorties : Chaque paire est considérée par ELFE comme un équipement domotique indépendant.
L'automate ne publie pas de LWT (Juin 23).
*/
CREATE TABLE equipement_domotique_socorel_automate_v0 (
  id text NOT NULL, /* ID de la ligne */
  equipement_domotique_id text NOT NULL, /* ID de equipement_domotique */
  topic_mqtt_controle_json text NOT NULL, /* topic MQTT qui donne un JSON contenant les états de controle */
  topic_mqtt_commande_text text NOT NULL, /* topic MQTT générique dans lequel on envoie une commande sous forme de texte */
  topic_mqtt_lwt text NOT NULL /* topic MQTT Last Will and Testament */
);

ALTER TABLE ONLY equipement_domotique_socorel_automate_v0 ADD CONSTRAINT equipement_domo_socorel_automate_v0_id_pkey PRIMARY KEY (id);
ALTER TABLE ONLY equipement_domotique_socorel_automate_v0 ADD CONSTRAINT equipement_domo_socorel_automate_v0_eq_dom_id_fkey FOREIGN KEY (equipement_domotique_id) REFERENCES equipement_domotique(id) ON UPDATE CASCADE ON DELETE RESTRICT;



-- #################### Partie finale - Privilèges
--

-- GRANT ALL PRIVILEGES ON DATABASE preprod_bdd_coordination TO ems,viriya,commande,coordination;
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA bdd_coordination_schema TO ems,viriya,commande,coordination;
-- GRANT ALL PRIVILEGES ON SCHEMA bdd_coordination_schema TO ems,viriya,commande,coordination;
-- grant all privileges on all sequences in schema bdd_coordination_schema to viriya,ems,commande,coordination;

-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO ems,viriya,commande,coordination;
-- GRANT ALL PRIVILEGES ON SCHEMA public TO ems,viriya,commande,coordination;
-- GRANT ALL PRIVILEGES ON ALL sequences in schema public to viriya,ems,commande,coordination;


/* quitter
\q
*/

/* RAZ
export PGSQL_DB_NAME=bdd_coordination
export PGSQL_USERNAME=user_elfe_bdd
export PGSQL_USERPWD="FJdfskj^qsdefk2I@SK"

/bin/su postgres --command "/usr/bin/psql --command=\"DROP DATABASE IF EXISTS ${PGSQL_DB_NAME};\""
/bin/su postgres --command "/usr/bin/psql --command=\"DROP SCHEMA IF EXISTS ${PGSQL_DB_NAME};\""
/bin/su postgres --command "/usr/bin/psql --command=\"DROP user IF EXISTS ${PGSQL_USERNAME};\""

cd /
/bin/su postgres --command "/usr/bin/createuser --no-superuser --no-createdb --no-createrole --login ${PGSQL_USERNAME}"
/bin/su postgres --command "/usr/bin/psql --command=\"ALTER USER ${PGSQL_USERNAME} PASSWORD '${PGSQL_USERPWD}'\""
/bin/su postgres --command "/usr/bin/createdb --encoding UTF8 --owner ${PGSQL_USERNAME} ${PGSQL_DB_NAME}"
/bin/su postgres --command "/usr/bin/psql --command \"GRANT ALL PRIVILEGES ON DATABASE ${PGSQL_DB_NAME} to ${PGSQL_USERNAME}\""

// Supprimer les tables
DO $$
DECLARE
    r RECORD;
BEGIN
    FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = 'public') LOOP
        EXECUTE 'DROP TABLE IF EXISTS ' || quote_ident(r.tablename) || ' CASCADE';
    END LOOP;
END $$;

// Vider les tables sans supprimer le schéma ni tables !! Vide les énumérations :(
DO $$
DECLARE
    r RECORD;
BEGIN
    FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = 'bdd_coordination_schema') LOOP
        EXECUTE 'TRUNCATE TABLE ' || quote_ident(r.tablename) || ' CASCADE';
    END LOOP;
END $$;

 */
