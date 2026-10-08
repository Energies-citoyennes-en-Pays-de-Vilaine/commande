
import json

class configcore ():
    
    def __init__ (self):
        self.config = {
            'mqtt': {'host':'127.0.0.1', 'port':'', 'user':'', 'pass':''},
            'pgsql': {'host':'127.0.0.1', 'port':'', 'user':'', 'pass':''},
        }

    def load (self, path):
        try:
            with open(path) as f:
                data = json.load (f)
                self.config = data
        except:
            pass
    
    def save (self, path):
        with open (path, "w") as f:
            json.dump (self.config, f)

class config ():
    __config: configcore | None = None


    
    def get_current_config ():
        if config.__config is None:
            config.__config = configcore ()
        return config.__config

    @classmethod
    def set_current_config(cls, c: configcore | dict):
        match c:
            case dict():
                cls.__config = configcore()
                cls.__config.config = c
            case configcore():
                cls.__config = c

    def load (self, path):
        if not config.__config is None:
            config.__config.load (path)

    def save (self, path):
        if not config.__config is None:
            config.__config.save (path)
