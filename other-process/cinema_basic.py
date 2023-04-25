from MysqlConnector import MysqlConnector
from ConfigHelper import Config


def update_affection():
    output_connector = MysqlConnector()
    config = Config()
    config.read_config_src('general.ini')
    target_year = int(config.config_parser.get('General', 'target_year'))
    output_connector.connect(database='filmdom_output_%d' % int(target_year))
    sql = 'SELECT MAX(AvgShowPeople), MAX(AudienceCount) FROM 艺恩影院年票房'
    data_set = output_connector.search(sql)
    max_avg_view = float(data_set[0][0])
    max_audience_count = int(data_set[0][1])

    sql = 'SELECT id FROM cinema_basic'
    cinema_list = output_connector.search(sql)
    for cinema in cinema_list:
        cinema_id = int(cinema[0])
        sql = 'SELECT AvgShowPeople, AudienceCount FROM 艺恩影院年票房 WHERE CinemaCode="%d" AND year="%d"' \
              % (cinema_id, target_year)
        data = output_connector.search(sql)
        # 基于场均观影人次和观影人次计算喜爱度
        if data is None or data == ():
            continue
        audience_score = (int(data[0][1]) / max_audience_count) * 4.0
        avg_audience_score = (float(data[0][0]) / max_avg_view) * 6.0
        affection = audience_score + avg_audience_score
        sql = 'UPDATE cinema_basic SET affection="%f" WHERE id="%d"' % (affection, cinema_id)
        output_connector.execute(sql)
    output_connector.close()


if __name__ == '__main__':
    update_affection()