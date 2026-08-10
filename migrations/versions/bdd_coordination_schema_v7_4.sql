set search_path to bdd_coordination_schema, public;

create table cofybox (
    id text primary key not null
);

alter table equipement_domotique add cofybox_id text not null references cofybox(id);
