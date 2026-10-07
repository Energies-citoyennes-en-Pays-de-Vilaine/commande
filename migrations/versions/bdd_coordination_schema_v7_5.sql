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
