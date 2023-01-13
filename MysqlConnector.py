import pymysql
from ConfigHelper import Config


class MysqlConnector:

    def __init__(self):
        self.connection = None
        self.cursor = None
        pass

    def connect(self, database: str, host=None, user=None, password=None, charset=None):
        try:
            if self.connection is not None:
                self.close()
            config = Config()
            config.set_config_src('database.ini')
            self.connection = pymysql.connect(
                host=config.config_parser.get('mysql', 'host'),
                user=config.config_parser.get('mysql', 'user'),
                password=config.config_parser.get('mysql', 'password'),
                database=database,
                charset=config.config_parser.get('mysql', 'charset'),
            )
            self.cursor = self.connection.cursor()
            print('mysql database: %s connected' % self.connection.db)

        except pymysql.Error as e:
            print('mysql database: %s connection failed with exception %d : %s' %
                  (self.connection.db, e.args[0], e.args[1]))
        finally:
            return self.connection is not None

    def close(self):
        try:
            self.connection.close()
            self.connection = None
        except pymysql.Error as e:
            print('mysql database: %s close failed with exception %d : %s' %
                  (self.connection.db, e.args[0], e.args[1]))
        finally:
            return self.connection is None
