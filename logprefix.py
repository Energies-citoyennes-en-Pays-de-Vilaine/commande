import logging

def classname(typeof):
    st = str(typeof)
    res = st.split('\'')
    if len(res) == 3:
        return res[1]
    return st

class LogPrefix ():
    def __init__(self, prefix, logger):
        self.logger = logger
        self.prefix = prefix

    def warning (self, str):
        self.logger.warning ("[{0}]:{1}".format (self.prefix, str))

    def info (self, str):
        self.logger.info("[{0}]:{1}".format (self.prefix, str))

    def error (self, str):        
        self.logger.error("[{0}]:{1}".format (self.prefix, str))

    def debug (self, str):        
        self.logger.debug("[{0}]:{1}".format (self.prefix, str))        