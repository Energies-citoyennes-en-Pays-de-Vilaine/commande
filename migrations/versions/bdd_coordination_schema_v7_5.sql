create table bdd_coordination_schema.utilisateur_plage_tarifaire_electricite (
    utilisateur_id text not null,
    jour text not null,
    debut time not null,
    fin time not null,
    prix text not null,
    primary key (utilisateur_id, jour, debut),
    foreign key (utilisateur_id) references bdd_coordination_schema.utilisateur (id)
);

create table bdd_coordination_schema.equipement_pilote_planning_chauffage (
    equipement_pilote_ou_mesure_id integer not null,
    jour text not null,
    debut time not null,
    fin time not null,
    mode text not null,
    primary key (equipement_pilote_ou_mesure_id, jour, debut),
    foreign key (equipement_pilote_ou_mesure_id) references bdd_coordination_schema.equipement_pilote_ou_mesure (id)
);

drop table bdd_coordination_schema.heures_creuses_utilisateur;
drop table bdd_coordination_schema.chauffage_planning_de_confort;

alter table bdd_coordination_schema.equipement_pilote_chauffage_non_asservi
    drop prog_semaine_periode_1_confort_actif,
    drop prog_semaine_periode_1_confort_heure_debut,
    drop prog_semaine_periode_1_confort_heure_fin,
    drop prog_semaine_periode_2_confort_actif,
    drop prog_semaine_periode_2_confort_heure_debut,
    drop prog_semaine_periode_2_confort_heure_fin,
    drop prog_weekend_periode_1_confort_actif,
    drop prog_weekend_periode_1_confort_heure_debut,
    drop prog_weekend_periode_1_confort_heure_fin,
    drop prog_weekend_periode_2_confort_actif,
    drop prog_weekend_periode_2_confort_heure_debut,
    drop prog_weekend_periode_2_confort_heure_fin;
