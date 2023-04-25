from MysqlConnector import MysqlConnector
from ConfigHelper import Config


def append():
    output_connector = MysqlConnector()
    raw_connector = MysqlConnector()
    config = Config()
    config.read_config_src('general.ini')
    target_year = int(config.config_parser.get('General', 'target_year'))
    output_connector.connect(database='filmdom_output_%d' % int(target_year))
    sql = 'SELECT mid, film_name, film_id FROM movies WHERE year=2022'
    movies = output_connector.search(sql)
    raw_connector.connect()
    for movie in movies:
        mmid = int(movie[0])
        film_name = movie[1]
        film_id = int(movie[2])
        sql = 'SELECT * FROM movies_box_day WHERE mmid="%d"' % mmid
        box_info_list = raw_connector.search(sql)
        if box_info_list is None:
            continue
        count = 0
        for box_info in box_info_list:
            if count > 30:
                break
            box_date = box_info[1]
            box = box_info[2]
            if box == 0:
                continue
            sql = 'INSERT IGNORE INTO movie_day_boxoffice SET film_id="%d", release_date="%s", film_name="%s", box_office="%s", ' \
                  'year="%d"' % (film_id, box_date, film_name, box, target_year)
            output_connector.execute(sql)
            count += 1
    raw_connector.close()
    output_connector.close()


if __name__ == '__main__':
    append()