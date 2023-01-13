import configparser
import os


class Config(object):
    # Thread safe configure read and write class
    _config_root = os.path.dirname(os.path.abspath(__file__)) + '\\configs\\'
    config_parser = configparser.ConfigParser()

    def __init__(self):
        pass

    def set_config_src(self, config_name, encoding='utf-8'):
        self.config_parser.read(self._config_root + config_name,
                                encoding=encoding)

