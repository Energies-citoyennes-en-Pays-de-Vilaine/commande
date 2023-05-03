#!/home/sgodin/dev/work/elfe/commande/venv/bin python3

import logging
import os
import time
import systemhandler
import config
import broker
import ems
import elfeconstant


config = config.config.get_current_config ()
_vars = {
    elfeconstant.ENV_BROKER_PWD:["mqtt", "pass"], 
    elfeconstant.ENV_BROKER_USER:["mqtt", "user"], 
    elfeconstant.ENV_DATABASE_PWD:["pgsql", "pass"], 
    elfeconstant.ENV_DATABASE_USER:["pgsql", "user"]
}

def checkvar ():
    for var in _vars:
        if not var in os.environ:
            logging.error ("variable:{0}  not defined".format (var))
            exit(1)

def setvar ():
    for var,tags in _vars.items():
        
        config.config[tags[0]][tags[1]] = os.environ[var]

def main ():
    #init logger
    root_logger = logging.getLogger()
    root_logger.setLevel("INFO")
    root_logger.addHandler(systemhandler.SystemdHandler())

    logging.info ("commande start")

    #load config
    config.load ("./config.json")
    logging.info ("config loaded")
    
    #check env var
    checkvar ()
    setvar ()

    #start service
    root_logger.setLevel(config.config["logging"]["level"])
    broker.start ()
    ems.start ()
    
    while True:
        logging.info ("commande running")
        time.sleep(360)

#if __name__ == "__main__":
#    main ()
main ()