begin;

    update equipement_domotique_nous_a1t_tasmota_v12 edn
    set
    	topic_mqtt_commande_text = format('cmnd/%s/POWER', edn.equipement_domotique_id),
    	topic_mqtt_controle_json = format('stat/%s/RESULT', edn.equipement_domotique_id),
    	topic_mqtt_lwt = format('tele/%s/LWT', edn.equipement_domotique_id);

    update equipement_domotique_shellyplus1pm_shellycloud_v1 eds
    set
    	topic_mqtt_controle_et_mesure_json = format('shelly/%s/status/switch:0', eds.equipement_domotique_id),
    	topic_mqtt_commande_json = format('shelly/%s/rpc', eds.equipement_domotique_id),
    	topic_mqtt_lwt = format('shelly/%s/online', eds.equipement_domotique_id);

    delete from equipement_domotique_xky_tasmota_v12 edx
    where edx.id not like 'X%';

    update equipement_domotique_xky_tasmota_v12 edx
    set
    	topic_mqtt_controle_json = format('xky/%s/tele/SENSOR', edx.equipement_domotique_id),
    	topic_mqtt_commande_text = '',
    	topic_mqtt_lwt = format('xky/%s/tele/LWT', edx.equipement_domotique_id);

commit;
