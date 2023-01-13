from MysqlConnector import MysqlConnector
from ConfigHelper import Config


def init_database(year, connector):
    sql = "CREATE DATABASE IF NOT EXISTS Filmdom_Raw_" + year + \
          " DEFAULT CHARACTER SET utf8 DEFAULT COLLATE utf8_general_ci;"
    if connector.execute(sql):
        print('Database for raw data created')
        return True
    else:
        return False


def table_movies_to_fetch(connector):
    sql = "CREATE TABLE IF NOT EXISTS movies_to_fetch {" \
          " mid int(7) NOT NULL," \
          " name_zh varchar(20) NOT NULL" \
          " fetched int(1) NOT NULL"


if __name__ == '__main__':
    config = Config()
    config.set_config_src('general.ini')
    target_year = config.config_parser.get('General', 'target_year')
    connector = MysqlConnector()
    connector.connect()
    # Sql need to be execute
    # if database initialized, write config
    if init_database(target_year, connector):
        config.set_config_src('database.ini')
        config.config_parser.set('Mysql', 'database', )
    connector.close()
    table_movies_to_fetch(connector)

    # Sql execute end, close connection

