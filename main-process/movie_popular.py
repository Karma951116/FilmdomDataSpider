from MysqlConnector import MysqlConnector
from ConfigHelper import Config


def append():
    connector = MysqlConnector()
    config = Config()
    config.read_config_src('general.ini')
    target_year = int(config.config_parser.get('General', 'target_year'))
    connector.connect(database='filmdom_output_%d' % target_year)
    sql = 'SELECT film_name, film_id, country, box_office FROM movies WHERE year="%d"' % target_year
    movies = connector.search(sql)
    for movie in movies:
        film_name = movie[0]
        film_id = int(movie[1])
        country = movie[2]
        box = float(movie[3])
        url = 'http://192.168.100.72/movie/%d/' % film_id
        is_domestic = 1 if '中国' in country else 0
        box = round(box / 10000 / 10000, 2)
        sql = 'INSERT IGNORE INTO 影片_最受欢迎影片 SET 年份="%d", 影片名称="%s", 链接地址="%s", 是否为国产片="%d", ' \
              '票房数量（亿）="%f"' % (target_year, film_name, url, int(is_domestic), float(box))
        connector.execute(sql)
    connector.close()


if __name__ == '__main__':
    append()

