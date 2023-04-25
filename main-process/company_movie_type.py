from MysqlConnector import MysqlConnector
from ConfigHelper import Config


def append():
    connector = MysqlConnector()
    config = Config()
    config.read_config_src('general.ini')
    target_year = int(config.config_parser.get('General', 'target_year'))
    connector.connect(database='filmdom_output_%d' % target_year)
    sql = 'SELECT film_id, genre FROM movies WHERE year = %d' % target_year
    ret = connector.search(sql)
    ret_map = {}
    for item in ret:
        type_list = item[1].split(',')
        sql = 'SELECT COUNT(company_id) FROM movie_company WHERE film_id = %d' % item[0]
        count = int(connector.search(sql)[0][0])
        if count == 0:
            continue
        for type in type_list:
            if type.strip() in ret_map.keys():
                ret_map[type.strip()] += int(count)
            else:
                ret_map[type.strip()] = int(count)
    for item in ret_map:
        sql = 'INSERT INTO 制作公司_影片类型查看制作公司数量(年份, 影片类型, 制作公司数量) VALUES(%d, "%s", %d)' % \
              (target_year, item, int(ret_map[item]))
        connector.execute(sql)
    connector.close()


if __name__ == '__main__':
    append()
