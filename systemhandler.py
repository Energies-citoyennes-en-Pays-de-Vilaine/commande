import logging
import sys
from datetime import datetime

class SystemdHandler(logging.Handler):
    # https://0pointer.de/public/systemd-man/sd-daemon.html
    PREFIX = {
        # EMERG <0>
        # ALERT <1>
        logging.CRITICAL: "<2>",
        logging.ERROR: "<3>",
        logging.WARNING: "<4>",
        # NOTICE <5>
        logging.INFO: "<6>",
        logging.DEBUG: "<7>",
        logging.NOTSET: "<7>"
    }

    def __init__(self, stream=sys.stdout):
        self.stream = stream
        self.displaydate = False
        logging.Handler.__init__(self)

    def setDisplayDate (self, display):
        self.displaydate = display
        
    def emit(self, record):
        try:
            if self.displaydate:
                msg = datetime.now().strftime('%Y-%m-%d %H:%M:%S') + " " + self.PREFIX[record.levelno] + self.format(record) + "\n"
            else:
                msg = self.PREFIX[record.levelno] + self.format(record) + "\n"
            self.stream.write(msg)
            self.stream.flush()
        except Exception:
            self.handleError(record)
