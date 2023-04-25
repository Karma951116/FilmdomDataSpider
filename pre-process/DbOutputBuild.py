from MysqlConnector import MysqlConnector
from ConfigHelper import Config


def init_database(year, connector):
    sql = "CREATE DATABASE IF NOT EXISTS `filmdom_output_" + year + \
          "` DEFAULT CHARACTER SET utf8 DEFAULT COLLATE utf8_general_ci;"
    if connector.execute(sql):
        print('Database for output data created')
        return True
    else:
        return False


def copy_movies(previous_year, year, connector, database=None):
    sql = "CREATE TABLE IF NOT EXISTS `movies` SELECT * FROM "
    sql += "filmdom_output_%d" % int(previous_year) if database is None else database
    sql += ".movies"

    if connector.execute(sql):
        print('Table for movies output created')
        return True
    else:
        return False


def copy_movie_company(previous_year, year, connector, database=None):
    sql = "CREATE TABLE IF NOT EXISTS `movie_company` SELECT * FROM "
    sql += "filmdom_output_%d" % int(previous_year) if database is None else database
    sql += ".movie_company"

    if connector.execute(sql):
        print('Table for movie_company output created')
        return True
    else:
        return False


def copy_movies_day_box(previous_year, year, connector, database=None):
    sql = "CREATE TABLE IF NOT EXISTS `movie_day_boxoffice` SELECT * FROM "
    sql += "filmdom_output_%d" % int(previous_year) if database is None else database
    sql += ".movie_day_boxoffice"

    if connector.execute(sql):
        print('Table for movie_day_boxoffice output created')
        return True
    else:
        return False


def copy_company_basic(previous_year, year, connector, database=None):
    sql = "CREATE TABLE IF NOT EXISTS `company_basic` SELECT * FROM "
    sql += "filmdom_output_%d" % int(previous_year) if database is None else database
    sql += ".company_basic"

    if connector.execute(sql):
        print('Table for company_basic output created')
        return True
    else:
        return False


def copy_actors(previous_year, year, connector, database=None):
    sql = "CREATE TABLE IF NOT EXISTS `actors` SELECT * FROM "
    sql += "filmdom_output_%d" % int(previous_year) if database is None else database
    sql += ".actors"

    if connector.execute(sql):
        print('Table for actors output created')
        return True
    else:
        return False


def copy_actors_heat(previous_year, year, connector, database=None):
    sql = "CREATE TABLE IF NOT EXISTS `baidu_heat` SELECT * FROM "
    sql += "filmdom_output_%d" % int(previous_year) if database is None else database
    sql += ".baidu_heat"

    if connector.execute(sql):
        print('Table for baidu_heat output created')
        return True
    else:
        return False


def copy_co_actors(previous_year, year, connector, database=None):
    sql = "CREATE TABLE IF NOT EXISTS `co_actors` SELECT * FROM "
    sql += "filmdom_output_%d" % int(previous_year) if database is None else database
    sql += ".co_actors"

    if connector.execute(sql):
        print('Table for co_actors output created')
        return True
    else:
        return False


def copy_movie_box_statistics(previous_year, year, connector, database=None):
    sql = "CREATE TABLE IF NOT EXISTS `影片_票房统计` SELECT * FROM "
    sql += "filmdom_output_%d" % int(previous_year) if database is None else database
    sql += ".影片_票房统计"

    if connector.execute(sql):
        print('Table for 影片_票房统计 output created')
        return True
    else:
        return False


def copy_movie_popular(previous_year, year, connector, database=None):
    sql = "CREATE TABLE IF NOT EXISTS `影片_最受欢迎影片` SELECT * FROM "
    sql += "filmdom_output_%d" % int(previous_year) if database is None else database
    sql += ".影片_最受欢迎影片"

    if connector.execute(sql):
        print('Table for 影片_最受欢迎影片 output created')
        return True
    else:
        return False


def copy_movie_popular_participants(previous_year, year, connector, database=None):
    sql = "CREATE TABLE IF NOT EXISTS `影片_最受欢迎影星和导演` SELECT * FROM "
    sql += "filmdom_output_%d" % int(previous_year) if database is None else database
    sql += ".影片_最受欢迎影星和导演"

    if connector.execute(sql):
        print('Table for 影片_最受欢迎影星和导演 output created')
        return True
    else:
        return False


def copy_movie_statistics(previous_year, year, connector, database=None):
    sql = "CREATE TABLE IF NOT EXISTS `影片_数据统计` SELECT * FROM "
    sql += "filmdom_output_%d" % int(previous_year) if database is None else database
    sql += ".影片_数据统计"

    if connector.execute(sql):
        print('Table for 影片_数据统计 output created')
        return True
    else:
        return False


def copy_company_lng_and_lat(previous_year, year, connector, database=None):
    sql = "CREATE TABLE IF NOT EXISTS `制作公司_散点经纬度` LIKE "
    sql += "filmdom_output_%d" % int(previous_year) if database is None else database
    sql += ".制作公司_散点经纬度"

    if connector.execute(sql):
        print('Table for 制作公司_散点经纬度 output created')
        return True
    else:
        return False


def copy_company_movie_type(previous_year, year, connector, database=None):
    sql = "CREATE TABLE IF NOT EXISTS `制作公司_影片类型查看制作公司数量` SELECT * FROM "
    sql += "filmdom_output_%d" % int(previous_year) if database is None else database
    sql += ".制作公司_影片类型查看制作公司数量"

    if connector.execute(sql):
        print('Table for 制作公司_影片类型查看制作公司数量 output created')
        return True
    else:
        return False


def copy_company_statistics(previous_year, year, connector, database=None):
    sql = "CREATE TABLE IF NOT EXISTS `制作公司_数据统计` SELECT * FROM "
    sql += "filmdom_output_%d" % int(previous_year) if database is None else database
    sql += ".制作公司_数据统计"

    if connector.execute(sql):
        print('Table for 制作公司_数据统计 output created')
        return True
    else:
        return False


def copy_overall_movies(previous_year, year, connector, database=None):
    sql = "CREATE TABLE IF NOT EXISTS `总览_上映影片` SELECT * FROM "
    sql += "filmdom_output_%d" % int(previous_year) if database is None else database
    sql += ".总览_上映影片"

    if connector.execute(sql):
        print('Table for 总览_上映影片 output created')
        return True
    else:
        return False


def copy_overall_statistics(previous_year, year, connector, database=None):
    sql = "CREATE TABLE IF NOT EXISTS `总览_数字统计` SELECT * FROM "
    sql += "filmdom_output_%d" % int(previous_year) if database is None else database
    sql += ".总览_数字统计"

    if connector.execute(sql):
        print('Table for 总览_数字统计 output created')
        return True
    else:
        return False


def copy_overall_week_and_day(previous_year, year, connector, database=None):
    sql = "CREATE TABLE IF NOT EXISTS `总览_影片统计_周和日` SELECT * FROM "
    sql += "filmdom_output_%d" % int(previous_year) if database is None else database
    sql += ".总览_影片统计_周和日"

    if connector.execute(sql):
        print('Table for 总览_影片统计_周和日 output created')
        return True
    else:
        return False


if __name__ == '__main__':
    config = Config()
    config.read_config_src('general.ini')
    target_year = config.config_parser.get('General', 'target_year')
    previous_year = int(target_year) - 1
    connector = MysqlConnector()
    connector.connect(False)
    init_database(target_year, connector)
    connector.connect(database='filmdom_output_%d' % int(target_year))
    if connector.connected():
        copy_company_basic(previous_year, target_year,
                           connector, database='2021data')
        copy_actors(previous_year, target_year,
                    connector, database='2021data')
        copy_movies(previous_year, target_year,
                    connector, database='2021data')
        copy_movie_company(previous_year, target_year,
                           connector, database='2021data')
        copy_movies_day_box(previous_year, target_year,
                            connector, database='2021data')
        copy_co_actors(previous_year, target_year,
                       connector, database='2021data')
        copy_movie_box_statistics(previous_year, target_year,
                                  connector, database='2021data')
        copy_movie_popular(previous_year, target_year,
                           connector, database='2021data')
        copy_movie_popular_participants(previous_year, target_year,
                                        connector, database='2021data')
        copy_company_lng_and_lat(previous_year, target_year,
                                 connector, database='2021data')
        copy_company_movie_type(previous_year, target_year,
                                connector, database='2021data')
        copy_overall_movies(previous_year, target_year,
                            connector, database='2021data')
        copy_overall_statistics(previous_year, target_year,
                                connector, database='2021data')
        copy_overall_week_and_day(previous_year, target_year,
                                  connector, database='2021data')
        copy_company_statistics(previous_year, target_year,
                                connector, database='2021data')
        copy_movie_statistics(previous_year, target_year,
                              connector, database='2021data')
        copy_actors_heat(previous_year, target_year,
                              connector, database='2021data')
    connector.close()
