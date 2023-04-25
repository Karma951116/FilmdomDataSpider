from MysqlConnector import MysqlConnector
from ConfigHelper import Config


def append():
    connector = MysqlConnector()
    config = Config()
    config.read_config_src('general.ini')
    target_year = int(config.config_parser.get('General', 'target_year'))
    connector.connect()
    sql = 'SELECT mmid, SUM(avg_view * show_count) FROM movies_box_day GROUP BY mmid'
    ret = connector.search(sql)
    connector.close()
    connector.connect(database='filmdom_output_%d' % target_year)
    mmid_view_map = {}
    for item in ret:
        mmid_view_map[int(item[0])] = int(item[1])
    director_rank = {}
    actor_rank = {}
    sql = 'SELECT mid, director_id, actor_id FROM movies WHERE year="%d"' % target_year
    movies = connector.search(sql)
    for movie in movies:
        mmid = int(movie[0])
        view_count = int(mmid_view_map[mmid]) if mmid in mmid_view_map.keys() else 0
        director_list = movie[1].split(',')
        for director in director_list:
            if director == '':
                continue
            if int(director) not in director_rank.keys():
                director_rank[int(director)] = view_count
            else:
                director_rank[int(director)] += view_count
        actor_list = movie[2].split(',')
        for actor in actor_list:
            if actor == '' or int(actor) == 3063395 or int(actor) == 3063393 or int(actor) == 3063392:
                continue
            if int(actor) not in actor_rank.keys():
                actor_rank[int(actor)] = view_count
            else:
                actor_rank[int(actor)] += view_count
    director_rank = zip(director_rank.values(), director_rank.keys())
    director_rank = sorted(director_rank)
    director_rank.reverse()
    director_rank = director_rank[:50]
    actor_rank = zip(actor_rank.values(), actor_rank.keys())
    actor_rank = sorted(actor_rank)
    actor_rank.reverse()
    actor_rank = actor_rank[:50]
    director_rank = add_rank(director_rank)
    actor_rank = add_rank(actor_rank)

    sql = 'SELECT name, mid FROM actors'
    ret = connector.search(sql)
    name_mid_map = {}
    for item in ret:
        name_mid_map[int(item[1])] = item[0]

    for director in director_rank:
        director_id = int(director[1])
        director_name = name_mid_map[director_id]
        d_rank = int(director[2])
        url = 'http://192.168.100.72/actor/%d/' % director_id
        sql = 'INSERT IGNORE INTO 影片_最受欢迎影星和导演 SET 年份="%d", 排名="%d", 导演="%s", 导演链接地址="%s"' \
              % (target_year, d_rank, director_name, url)
        connector.execute(sql)

    for actor in actor_rank:
        actor_id = int(actor[1])
        actor_name = name_mid_map[actor_id]
        a_rank = int(actor[2])
        url = 'http://192.168.100.72/actor/%d/' % actor_id
        sql = 'UPDATE 影片_最受欢迎影星和导演 SET 演员="%s", 演员链接地址="%s" WHERE 排名="%d" AND 年份="%d"' \
              % (actor_name, url, a_rank, target_year)
        connector.execute(sql)
    connector.close()


def add_rank(ordered_list):
    rank = 0
    fore_value = None
    ret_list = []
    for num in range(0, len(ordered_list)):
        cur_value = ordered_list[num][1]
        if cur_value != fore_value:
            rank += 1
        new_tuple = ordered_list[num] + (rank,)
        ret_list.append(new_tuple)
        fore_value = cur_value
    return ret_list


if __name__ == '__main__':
    append()


