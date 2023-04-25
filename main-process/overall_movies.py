from MysqlConnector import MysqlConnector
from ConfigHelper import Config


def append():
    connector = MysqlConnector()
    config = Config()
    config.read_config_src('general.ini')
    target_year = int(config.config_parser.get('General', 'target_year'))
    connector.connect(database='filmdom_output_%d' % target_year)
    sql = 'SELECT year, box_office, genre from movies'
    ret = connector.search(sql)
    genre_box_map = {}
    for item in ret:
        genre_list = str(item[2]).split(',')
        for genre in genre_list:
            if genre.strip() not in genre_box_map.keys():
                genre_box_map[genre.strip()] = float(item[1])
            else:
                genre_box_map[genre.strip()] += float(item[1])
    print(genre_box_map)
    for key in genre_box_map.keys():
        sql = 'INSERT INTO 总览_上映影片(年份, 影片类型, 影片票房数量)VALUES(%d, "%s", %f)' % \
              (target_year, key, genre_box_map[key])
        connector.execute(sql)
    connector.close()


if __name__ == '__main__':
    append()