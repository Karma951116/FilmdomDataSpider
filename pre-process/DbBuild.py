from MysqlConnector import MysqlConnector
from ConfigHelper import Config


def init_database(year, connector):
    sql = "CREATE DATABASE IF NOT EXISTS `filmdom_raw_" + year + \
          "` DEFAULT CHARACTER SET utf8 DEFAULT COLLATE utf8_general_ci;"
    if connector.execute(sql):
        print('Database for raw data created')
        return True
    else:
        return False


def table_movies_to_fetch(connector):
    sql = "CREATE TABLE IF NOT EXISTS `movies_to_fetch_from_maoyan` (" \
          "`mid` int(10) NOT NULL COMMENT 'maoyan id'," \
          "`name_zh` varchar(20) NOT NULL COMMENT 'film name in Chinese'," \
          "`fetched` int(1) NOT NULL COMMENT '0 for not fetched and 1 for fetched'," \
          "`fetch_time` int(20) NOT NULL COMMENT 'fetch time in timestamp(sec)'," \
          "PRIMARY KEY (`mid`)" \
          ") ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='Table for movies to be fetch';"
    if connector.execute(sql):
        print("Table 'movies_to_fetch' created")
        return True
    else:
        return False


def table_movie_base(connector):
    sql = "CREATE TABLE IF NOT EXISTS `movies_base` (" \
          "`mid` int(10) NOT NULL COMMENT 'maoyan id'," \
          "`name_zh` varchar(255) NOT NULL COMMENT 'film name in Chinese'," \
          "`name_en` varchar(255) NOT NULL COMMENT 'film name in English'," \
          "`release_date` varchar(255) NOT NULL," \
          "`duration` varchar(255) NOT NULL," \
          "`show_country` varchar(255)," \
          "`genre` varchar(255) NOT NULL," \
          "`product_country` varchar(255) NOT NULL," \
          ") ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='Table for movies basic information';"
    if connector.execute(sql):
        print("Table 'movies_base' created")
        return True
    else:
        return False


def table_movies_box_summary(connector):
    sql = "CREATE TABLE IF NOT EXISTS `movies_box_summary` (" \
          "`mid` int(10) NOT NULL COMMENT 'maoyan id'," \
          "`box_office` decimal(65, 2) NOT NULL COMMENT 'total box office in decimal'," \
          "`split_box_office` decimal(65, 2) COMMENT 'split box office in decimal'" \
          "`box_first_day` decimal(65, 2) COMMENT 'split box office in decimal'" \
          "`box_first_week` decimal(65, 2) COMMENT 'split box office in decimal'" \
          ") ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='Table for movies basic information';"
    if connector.execute(sql):
        print("Table 'movies_box_summary' created")
        return True
    else:
        return False


if __name__ == '__main__':
    config = Config()
    config.read_config_src('general.ini')
    target_year = config.config_parser.get('General', 'target_year')
    connector = MysqlConnector()
    connector.connect()
    # if database initialized, write config
    if init_database(target_year, connector):
        config.config_parser.clear()
        config.read_config_src('database.ini')
        config.config_parser.set('Mysql', 'database', "filmdom_raw_" + target_year)
        config.write_config_src('database.ini')
    connector.close()
    # reconnect database
    connector.connect()
    table_movies_to_fetch(connector)

    # Sql execute end, close connection
    connector.close()

