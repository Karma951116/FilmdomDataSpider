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
          "`mmid` int(10) NOT NULL COMMENT 'maoyan movie id'," \
          "`name_zh` varchar(255) NOT NULL COMMENT 'film name in Chinese'," \
          "`base_fetched` int(1) NOT NULL COMMENT '0:not fetched, 1:fetched, 2:no data'," \
          "`awards_fetched` int(1) NOT NULL," \
          "`participants_fetched` int(1) NOT NULL," \
          "`box_summary_fetched` int(1) NOT NULL," \
          "`box_day_fetched` int(1) NOT NULL," \
          "`ratings_fetched` int(1) NOT NULL," \
          "`wanted_fetched` int(1) NOT NULL," \
          "`douban_fetched` int(1) NOT NULL," \
          "`weibo_fetched` int(1) NOT NULL," \
          "`fetch_time` int(20) COMMENT 'fetch time in timestamp(sec)'," \
          "PRIMARY KEY (`mmid`)" \
          ") ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='Table for movies to be fetch';"
    if connector.execute(sql):
        print("Table 'movies_to_fetch_from_maoyan' created")
        return True
    else:
        return False


def table_movies_base(connector):
    sql = "CREATE TABLE IF NOT EXISTS `movies_base` (" \
          "`mmid` int(10) NOT NULL COMMENT 'maoyan movie id'," \
          "`name_zh` varchar(255) NOT NULL COMMENT 'film name in Chinese'," \
          "`name_en` varchar(255) NOT NULL COMMENT 'film name in English'," \
          "`release_date` varchar(255) NOT NULL," \
          "`duration` varchar(255) NOT NULL," \
          "`show_country` varchar(255)," \
          "`genre` varchar(255)," \
          "`product_country` varchar(255)," \
          "PRIMARY KEY (`mmid`)" \
          ") ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='Table for movies basic information';"
    if connector.execute(sql):
        print("Table 'movies_base' created")
        return True
    else:
        return False


def table_movies_awards(connector):
    sql = "CREATE TABLE IF NOT EXISTS `movies_awards` (" \
          "`mmid` int(10) NOT NULL COMMENT 'maoyan movie id'," \
          "`portrait` varchar(255) COMMENT 'award name'," \
          "`award` varchar(255) COMMENT 'award class'," \
          "`nominate` varchar(255)," \
          "PRIMARY KEY (`mmid`, `portrait`)" \
          ") ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='Table for movies award information';"
    if connector.execute(sql):
        print("Table 'movies_awards' created")
        return True
    else:
        return False


def table_movies_participants(connector):
    sql = "CREATE TABLE IF NOT EXISTS `movies_participants` (" \
          "`mmid` int(10) NOT NULL COMMENT 'maoyan movie id'," \
          "`type` varchar(255) COMMENT 'participant class'," \
          "`name` varchar(255)," \
          "`role` varchar(255)," \
          "`mpid` int(10) NOT NULL COMMENT 'maoyan participants id'," \
          "PRIMARY KEY (`mmid`, `mpid`)" \
          ") ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='Table for movies participants information';"
    if connector.execute(sql):
        print("Table 'movies_participants' created")
        return True
    else:
        return False


def table_movies_box_summary(connector):
    sql = "CREATE TABLE IF NOT EXISTS `movies_box_summary` (" \
          "`mmid` int(10) NOT NULL COMMENT 'maoyan movie id'," \
          "`box_office` varchar(255) COMMENT 'total box office in decimal'," \
          "`box_first_day` varchar(255) COMMENT 'split box office in decimal'," \
          "`box_first_week` varchar(255) COMMENT 'split box office in decimal'," \
          "PRIMARY KEY (`mmid`)" \
          ") ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='Table for movies summary boxoffice';"
    if connector.execute(sql):
        print("Table 'movies_box_summary' created")
        return True
    else:
        return False


def table_movies_box_day(connector):
    sql = "CREATE TABLE IF NOT EXISTS `movies_box_day` (" \
          "`mmid` int(10) NOT NULL COMMENT 'maoyan movie id'," \
          "`box_date` date NOT NULL," \
          "`box_office` varchar(255) NOT NULL COMMENT 'total box office in decimal'," \
          "`avg_view` varchar(255) COMMENT 'average view count'," \
          "`show_count` varchar(255)," \
          "PRIMARY KEY (`mmid`, `box_date`)" \
          ") ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='Table for movies day boxoffice';"
    if connector.execute(sql):
        print("Table 'movies_box_day' created")
        return True
    else:
        return False


def table_movies_ratings(connector):
    sql = "CREATE TABLE IF NOT EXISTS `movies_ratings` (" \
          "`mmid` int(10) NOT NULL COMMENT 'maoyan movie id'," \
          "`rating` double," \
          "`rating_count` int(10)," \
          "`five_star_rate` varchar(255),"\
          "`four_star_rate` varchar(255)," \
          "`three_star_rate` varchar(255)," \
          "`two_star_rate` varchar(255),"\
          "`one_star_rate` varchar(255)," \
          "`comparison` varchar(255)," \
          "`wanted` int(10)," \
          "PRIMARY KEY (`mmid`)" \
          ") ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='Table for movies ratings and wanted';"
    if connector.execute(sql):
        print("Table 'movies_ratings' created")
        return True
    else:
        return False


def table_movies_douban_weibo(connector):
    sql = "CREATE TABLE IF NOT EXISTS `movies_douban_weibo` (" \
          "`mmid` int(10) NOT NULL COMMENT 'maoyan movie id'," \
          "`dmid` int(10) COMMENT 'douban movie id'," \
          "`douban_num` varchar(255)," \
          "`douban_value` int(10),"\
          "`weibo_discussion` varchar(255)," \
          "`weibo_value` int(10)," \
          "PRIMARY KEY (`mmid`)" \
          ") ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='Table for movies douban and weibo informations';"
    if connector.execute(sql):
        print("Table 'movies_douban_weibo' created")
        return True
    else:
        return False


def table_participants_to_fetch(connector):
    sql = "CREATE TABLE IF NOT EXISTS `participants_to_fetch_from_maoyan` (" \
          "`mpid` int(10) NOT NULL COMMENT 'maoyan participant id'," \
          "`name_zh` varchar(255) NOT NULL COMMENT 'film name in Chinese'," \
          "`base_fetched` int(1) NOT NULL COMMENT '0:not fetched, 1:fetched, 2:no data'," \
          "`poster_fetched` int(1) NOT NULL," \
          "`awards_fetched` int(1) NOT NULL," \
          "`related_fetched` int(1) NOT NULL," \
          "`heat_province_fetched` int(1) NOT NULL," \
          "`heat_age_fetched` int(1) NOT NULL," \
          "`heat_gender_fetched` int(1) NOT NULL," \
          "`fetch_time` int(20) COMMENT 'fetch time in timestamp(sec)'," \
          "PRIMARY KEY (`mpid`)" \
          ") ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='Table for participants to be fetch';"
    if connector.execute(sql):
        print("Table 'participants_to_fetch_from_maoyan' created")
        return True
    else:
        return False


def table_participant_base(connector):
    sql = "CREATE TABLE IF NOT EXISTS `participant_base` (" \
          "`mpid` int(10) NOT NULL COMMENT 'maoyan participant id'," \
          "`name_zh` varchar(255) NOT NULL COMMENT 'name in Chinese'," \
          "`name_en` varchar(255)," \
          "`sex` varchar(255)," \
          "`jobs` varchar(255)," \
          "`born` varchar(255)," \
          "`birthday` varchar(255)," \
          "`introduce` varchar(255)," \
          "`nationality` varchar(255)," \
          "PRIMARY KEY (`mpid`)" \
          ") ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='Table for participant basic information';"
    if connector.execute(sql):
        print("Table 'participant_base' created")
        return True
    else:
        return False


def table_participant_award(connector):
    sql = "CREATE TABLE IF NOT EXISTS `participant_award` (" \
          "`mpid` int(10) NOT NULL COMMENT 'maoyan participant id'," \
          "`portrait` varchar(255)," \
          "`award` varchar(255)," \
          "`film` varchar(255)," \
          "`year` int(10)," \
          "`role` varchar(255)," \
          "PRIMARY KEY (`mpid`, `portrait`, `award`)" \
          ") ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='Table for participant award information';"
    if connector.execute(sql):
        print("Table 'participant_award' created")
        return True
    else:
        return False


def table_participant_related(connector):
    sql = "CREATE TABLE IF NOT EXISTS `participant_related` (" \
          "`mpid` int(10) NOT NULL COMMENT 'maoyan participant id'," \
          "`related_name` varchar(255) NOT NULL," \
          "`related_id` varchar(255) NOT NULL," \
          "`relation` varchar(255)," \
          "PRIMARY KEY (`mpid`, `related_id`)" \
          ") ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='Table for participant related information';"
    if connector.execute(sql):
        print("Table 'participant_related' created")
        return True
    else:
        return False


def table_participant_baidu_heat(connector):
    sql = "CREATE TABLE IF NOT EXISTS `participant_baidu_heat` (" \
          "`mpid` int(10) NOT NULL COMMENT 'maoyan participant id'," \
          "`name_zh` varchar(255) NOT NULL," \
          "`province_rate` varchar(255)," \
          "`age_rate` varchar(255)," \
          "`gender_rate` varchar(255)," \
          "PRIMARY KEY (`mpid`)" \
          ") ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='Table for participant baidu heat';"
    if connector.execute(sql):
        print("Table 'participant_baidu_heat' created")
        return True
    else:
        return False


if __name__ == '__main__':
    config = Config()
    config.read_config_src('general.ini')
    target_year = config.config_parser.get('General', 'target_year')
    config.config_parser.set('Mysql', 'database', "filmdom_raw_" + target_year)
    config.write_config_src('general.ini')

    connector = MysqlConnector()
    if not connector.connect():
        connector.connect(False)
    # if database initialized, write config
    if connector.connected():
        init_database(target_year, connector)
        # reconnect database
        connector.connect()
        table_movies_to_fetch(connector)
        table_movies_base(connector)
        table_movies_awards(connector)
        table_movies_participants(connector)
        table_movies_box_summary(connector)
        table_movies_box_day(connector)
        table_movies_ratings(connector)
        table_participants_to_fetch(connector)
        table_participant_base(connector)
        table_participant_award(connector)
        table_participant_related(connector)
        table_participant_baidu_heat(connector)
        table_movies_douban_weibo(connector)
        # Sql execute end, close connection
        connector.close()


