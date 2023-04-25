from MysqlConnector import MysqlConnector
from ConfigHelper import Config


def append():
    connector = MysqlConnector()
    config = Config()
    config.read_config_src('general.ini')
    target_year = int(config.config_parser.get('General', 'target_year'))
    connector.connect(database='filmdom_output_%d' % target_year)
    sql = 'SELECT film_name, genre, box_office, film_id FROM movies WHERE year="%d"' % target_year
    movies = connector.search(sql)
    for movie in movies:
        year = target_year
        name = movie[0]
        box = float(movie[2])
        film_id = int(movie[3])
        genres = movie[1].split('，')
        url = 'http://192.168.100.72/movie/%d/' % film_id
        for genre in genres:
            sql = 'INSERT IGNORE INTO 影片_票房统计 SET 年份="%d", 影片类型="%s", 影片名称="%s", 票房数量="%f", 链接地址="%s"' \
                  % (year, genre.strip(), name, box, url)
            connector.execute(sql)
    connector.close()


if __name__ == '__main__':
    append()