from MysqlConnector import MysqlConnector
from ConfigHelper import Config


# 需要提前准备艺恩影院月票房表
def append():
    connector = MysqlConnector()
    config = Config()
    config.read_config_src('general.ini')
    target_year = int(config.config_parser.get('General', 'target_year'))
    connector.connect(database='filmdom_output_%d' % target_year)
    sql = 'SELECT province, InsertDate, SUM(AudienceCount), SUM(BoxOffice) FROM `艺恩影院月票房_2020` ' \
          'WHERE year = 2022 GROUP BY province, InsertDate'
    ret = connector.search(sql)
    for item in ret:
        date = item[1]
        date = date.replace('年', '-')
        date = date.replace('月', '')
        year = date.split('-')[0]
        month = date.split('-')[1]
        if len(month) == 1:
            month = '0' + str(month)
        date = '%s-%s' % (year, month)
        sql = 'INSERT IGNORE INTO 影片_数据统计 SET 年份="%d", 年月="%s", 省份_简称="%s", 观影人次="%s", 票房数量="%s"' \
              % (target_year, date, item[0], item[2], item[3])
        connector.execute(sql)
    connector.close()


def update_province_shortname():
    connector = MysqlConnector()
    config = Config()
    config.read_config_src('general.ini')
    target_year = int(config.config_parser.get('General', 'target_year'))
    connector.connect(database='filmdom_output_%d' % target_year)
    sql = 'SELECT 省份_简称 FROM 影片_数据统计 WHERE 年份!=2022 GROUP BY 省份_简称 '
    refer_set = connector.search(sql)
    refer = []
    for item in refer_set:
        refer.append(item[0])
    sql = 'SELECT 省份_简称 FROM 影片_数据统计 WHERE 年份=2022 GROUP BY 省份_简称 '
    test_set = connector.search(sql)
    defers = []
    for item in test_set:
        if item[0] not in refer:
            defers.append(item[0])

    for item in defers:
        for idx in range(2, len(item)):
            str = item[0: idx]
            for x in refer:
                if str in x:
                    sql = 'UPDATE 影片_数据统计 SET 省份_简称="%s" WHERE 省份_简称="%s" AND 年份="%d"' \
                          % (x, item, target_year)
                    connector.execute(sql)
    connector.close()

    connector.close()


if __name__ == '__main__':
    # append()
    update_province_shortname()
