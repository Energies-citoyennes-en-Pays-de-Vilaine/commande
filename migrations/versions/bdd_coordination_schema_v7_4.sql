set search_path to bdd_coordination_schema, public;

create table equipement_domotique_cofybox_hems_v2 (
    id text primary key not null,
    topic_mqtt_bridge text not null
);

insert into equipement_domotique_type (id, nom, nom_humain, description) values (911, 'cofybox_hems_v2','CofyBox - HEMS 2.0','Raspberry Pi sur lequel est déployée la suite HEMS 2.0 avec l''interface Home Assistant');
