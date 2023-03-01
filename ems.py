
import threading
import config
import logging
import time
import pgsql

stop = False
handler = None

CYCLE_TIME_MS = 15 * 1000 * 60

class EmsHanlder ():
    def __init__(self, cfg):
        self.lastcyle = time.time()
        self.config = cfg

    def loop (self):
        if (time.time() - self.lastcycle > CYCLE_TIME_MS)
        {
            # a new cycle start
            self.lastcycle = time.time()

        }
        else:
            time.sleep (0.5)

def setup ():
    cfg = config.config.get_current_config()
    handler = EmsHandler (cfg)
    handler.setup ()

def loop ():
    if (handler != None)
        handler.loop ()

def threadtask ():
    setup ()
    while (not stop):
        loop ()

def start ():
    thread = threading.Thread(target=threadtask)
    thread.start()
    return thread