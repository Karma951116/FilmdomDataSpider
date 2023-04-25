from MysqlConnector import MysqlConnector
from ConfigHelper import Config


def append():
    output_connector = MysqlConnector()
    raw_connector = MysqlConnector()
    config = Config()
    config.read_config_src('general.ini')
    target_year = int(config.config_parser.get('General', 'target_year'))
    output_connector.connect(database='filmdom_output_%d' % int(target_year))
    raw_connector.connect()
    sql = 'SELECT mpid FROM filmdom_raw_2022.participant_related as a WHERE NOT EXISTS ' \
          '(SELECT * FROM filmdom_output_2022.co_actors as b WHERE a.mpid = b.id) GROUP BY mpid'
    participants_list = raw_connector.search(sql)
    for participant in participants_list:
        mpid = int(participant[0])
        sql = 'SELECT name FROM actors WHERE mid="%d"' % mpid
        participant_name = output_connector.search(sql)[0][0]
        sql = 'SELECT * FROM participant_related WHERE mpid="%d"' % mpid
        related_list = raw_connector.search(sql)
        if related_list is None:
            continue
        co_actors = ''
        co_actors_id = ''
        relative = ''
        for relate in related_list:
            co_actors += relate[1] + ','
            co_actors_id += str(relate[2]) + ','
            relative += relate[3] + ','
        co_actors = co_actors.rstrip(',')
        co_actors_id = co_actors_id.rstrip(',')
        relative = relative.rstrip(',')
        sql = 'INSERT IGNORE INTO co_actors SET name="%s", id="%d", co_actors="%s", co_actorsID="%s", co_relative="%s"' \
              % (participant_name, mpid, co_actors, co_actors_id, relative)
        output_connector.execute(sql)
    raw_connector.close()
    output_connector.close()


if __name__ == '__main__':
    append()
