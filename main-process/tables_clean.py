from MysqlConnector import MysqlConnector
from ConfigHelper import Config

tables = ['actors', 'co_actors', 'company_basic', 'movie_company', 'movie_day_boxoffice', 'movies', '影片_票房统计',
          '影片_最受欢迎影片', '影片_最受欢迎影星和导演', '制作公司_散点经纬度', '制作公司_数据统计', '制作公司_影片类型查看制作公司数量',
          '总览_上映影片', '总览_数字统计', '总览_影片统计_周和日']


def clean():
    output_connector = MysqlConnector()
    config = Config()
    config.read_config_src('general.ini')
    target_year = int(config.config_parser.get('General', 'target_year'))
    output_connector.connect(database='filmdom_output_%d' % target_year)
    for table in tables:
        sql = 'SELECT COLUMN_NAME FROM information_schema.COLUMNS ' \
              'WHERE TABLE_SCHEMA ="filmdom_output_%d" AND TABLE_NAME ="%s"' % (target_year, table)
        columns = output_connector.search(sql)
        for column in columns:
            sql = 'UPDATE %s SET %s=NULL WHERE %s="None" or %s=""' % (table, column[0], column[0], column[0])
            output_connector.execute(sql)
    output_connector.close()


if __name__ == '__main__':
    clean()