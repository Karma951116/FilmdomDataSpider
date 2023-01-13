import pymysql
from ConfigHelper import Config


class MysqlConnector:

    def __init__(self):
        self.connection = None
        self.cursor = None
        pass

    def connect(self, host=None, user=None,
                password=None, database=None, charset=None):
        try:
            if self.connection is not None:
                self.connection.close()
            config = Config()
            config.read_config_src('database.ini')
            self.connection = pymysql.connect(
                host=config.config_parser.get('Mysql', 'host'),
                user=config.config_parser.get('Mysql', 'user'),
                password=config.config_parser.get('Mysql', 'password'),
                database=config.config_parser.get('Mysql', 'database'),
                charset=config.config_parser.get('Mysql', 'charset'),
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

    def search(self, sql):
        try:
            self.cursor.execute(sql)
            return self.cursor.fetchall()
        except pymysql.Error as e:
            print('Sql search failed with %d : %s' % (e.args[0], e.args[1]))
            return False

    def execute(self, sql):
        try:
            self.cursor.execute(sql)
            self.connection.commit()
            return True
        except pymysql.Error as e:
            print('Sql execute failed with %d : %s' % (e.args[0], e.args[1]))
            self.connection.rollback()
            return False

