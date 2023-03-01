#!/home/sgodin/dev/work/elfe/commande/venv/bin python3

import logging
import sys
import time
import systemhandler
import config
import broker

config = config.config.get_current_config ()


def main ():
    #init logger
    root_logger = logging.getLogger()
    root_logger.setLevel("INFO")
    root_logger.addHandler(systemhandler.SystemdHandler())

    logging.info ("commande start")

    #save config
    config.load ("./config.json")
    #config.save ("./config.json")
    logging.info ("config loaded")
    logging.info (config.config)
    
    broker.start ();

    while True:
        logging.info ("commande running")
        time.sleep(360)

if __name__ == "__main__":
    main ()