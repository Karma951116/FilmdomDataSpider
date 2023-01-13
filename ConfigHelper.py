import configparser
import os


class Config(object):
    # configure read/write class
    _config_root = os.path.dirname(os.path.abspath(__file__)) + '\\configs\\'
    config_parser = configparser.ConfigParser()

    def __init__(self):
        pass

    def read_config_src(self, config_name, encoding='utf-8'):
        """
        Append the config that read from file to configparser
        :param config_name: config file name (not absolute path)
        :param encoding: default utf-8
        :return: success ? True : False
        """
        ret = self.config_parser.read(self._config_root + config_name,
                                      encoding=encoding)
        if len(ret) > 0:
            print("Config load for %s complete" % config_name)
            return True
        else:
            return False

    def write_config_src(self, config_name):
        """
        Write all config that has been read to file
        :param config_name: config file name (not absolute path)
        :return: no return
        """
        with open(self._config_root + config_name, 'w') as f:
            self.config_parser.write(f)

