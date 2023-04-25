from MysqlConnector import MysqlConnector
from ConfigHelper import Config


# main-process order : 3
def append_actors():
    connector = MysqlConnector()
    config = Config()
    config.read_config_src('general.ini')
    target_year = config.config_parser.get('General', 'target_year')
    # Get max company number

    connector.connect()
    sql = 'SELECT * FROM participant_base'
    participants = connector.search(sql)

    actors_map = {}
    for participant in participants:
        mpid = int(participant[0])
        name_zh = participant[1]
        name_en = participant[2]
        sex = participant[3]
        jobs = participant[4]
        born = participant[5]
        birthday = participant[6]
        introduce = participant[7]
        if introduce is not None and '"' in introduce:
            introduce = introduce.replace('\"', '\\\"')

        job_list = jobs.split('|')
        jobs = ''
        for item in job_list:
            jobs += item.strip() + ' '
        jobs = jobs.rstrip(' ')

        sql = 'SELECT portrait, award, film FROM participant_award WHERE mpid="%d"' % mpid
        award_info = connector.search(sql)
        award_name = ''
        award_detail = ''
        award_film = ''
        for item in award_info:
            award_name += item[0] + ',' if item[0] is not None else ','
            award_detail += item[1] + ',' if item[1] is not None else ','
            award_film += item[2] + ',' if item[2] is not None else ','
        award_name = award_name.rstrip(',')
        if award_name is not None and '"' in award_name:
            award_name = award_name.replace('\"', '\\\"')
        award_detail = award_detail.rstrip(',')
        if award_detail is not None and '"' in award_detail:
            award_detail = award_detail.replace('\"', '\\\"')
        award_film = award_film.rstrip(',')
        if award_film is not None and '"' in award_film:
            award_film = award_film.replace('\"', '\\\"')
        actors_map[mpid] = (name_zh, name_en, sex, jobs, born, birthday, introduce, award_name, award_detail, award_film)
    connector.close()
    connector.connect(database='filmdom_output_%d' % int(target_year))
    sql = 'SELECT mid FROM actors'
    actor_id_tuple = connector.search(sql)
    actor_id_list = []
    for item in actor_id_tuple:
        actor_id_list.append(int(item[0]))
    for key in actors_map.keys():
        if int(key) not in actor_id_list:
            sql = 'INSERT IGNORE INTO actors SET name="%s", mid="%d", English_name="%s", sex="%s", jobs="%s", ' \
                  'born_from="%s", birthday="%s", introduction="%s", award_name="%s", award_detail="%s", award_movie="%s"' % \
                  (actors_map[key][0], key, actors_map[key][1], actors_map[key][2], actors_map[key][3],
                   actors_map[key][4], actors_map[key][5], actors_map[key][6], actors_map[key][7],
                   actors_map[key][8], actors_map[key][9])
            connector.execute(sql)
    connector.close()


if __name__ == '__main__':
    append_actors()
