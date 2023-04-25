from MysqlConnector import MysqlConnector
from ConfigHelper import Config

import random


# main-process order : 4
def append_movies():
    connector = MysqlConnector()
    config = Config()
    config.read_config_src('general.ini')
    target_year = int(config.config_parser.get('General', 'target_year'))
    connector.connect()
    # Get movies which box over 1M from raw database
    sql = 'SELECT * FROM movies_box_summary as A, movies_base as B WHERE A.box_office >= 1000000 AND A.mmid=B.mmid'
    movies = connector.search(sql)
    connector.close()
    # switch database to output
    connector.connect(database='filmdom_output_%d' % target_year)
    film_id_list = random_id(len(movies), target_year)
    for movie in movies:
        mmid = int(movie[0])
        box_office = movie[1]
        box_first_day = movie[2]
        box_first_week = movie[3]
        name_zh = movie[5]
        release_date = movie[7]
        duration = movie[8]
        genre = movie[10]
        product_country = movie[11]
        film_id = film_id_list[0]
        film_id_list.remove(film_id)

        genre = genre.replace(',', ' , ')

        sql = 'INSERT IGNORE INTO movies SET year="%d", film_name="%s", film_id="%d", box_office="%s", first_day="%s", ' \
              'first_week="%s", release_date="%s", mid="%d", run_time="%s", country="%s", genre="%s"' % \
              (int(target_year), name_zh, int(film_id), box_office, box_first_day, box_first_week, release_date, mmid,
               duration, product_country, genre)
        if not connector.execute(sql):
            print('FAILED append movies %d' % mmid)
    connector.close()


def random_id(count, year):
    id_list = []
    while id_list.__len__() < count:
        code = random.randint(1001, 9999)
        code_str = str(year) + str(code)
        if code_str not in id_list:
            id_list.append(code_str)
    return id_list


def update_rating():
    connector = MysqlConnector()
    config = Config()
    config.read_config_src('general.ini')
    target_year = int(config.config_parser.get('General', 'target_year'))
    connector.connect()
    sql = 'SELECT * FROM movies_ratings'
    ratings = connector.search(sql)
    connector.close()
    connector.connect(database='filmdom_output_%d' % target_year)
    for item in ratings:
        mmid = item[0]
        rating = item[1]
        rating_count = int(item[2]) if item[2] is not None else None
        five = item[3]
        four = item[4]
        three = item[5]
        two = item[6]
        one = item[7]
        comparison = item[8]
        wanted = int(item[9])

        if rating_count is not None and rating_count >= 10000:
            rating_count = str(float(rating_count / 10000)) + '万人评分'
        elif rating_count is not None and rating_count < 10000:
            rating_count = str(rating_count) + '人评分'

        better_than1 = None
        better_than2 = None
        better_than3 = None
        if comparison is not None:
            better_than_list = comparison.split(';')
            for x in better_than_list:
                if better_than1 is None:
                    better_than1 = x
                elif better_than2 is None:
                    better_than2 = x
                elif better_than3 is None:
                    better_than3 = x
        if wanted >= 10000:
            maoyan_wanted = str(float(wanted / 10000)) + "万"
        else:
            maoyan_wanted = str(wanted)

        sql = 'UPDATE movies SET rating="%s", rating_num="%s", five_stars="%s", four_stars="%s", three_stars="%s", ' \
              'two_stars="%s", one_stars="%s", maoyan_wanted="%s", maoyan_value="%s"' % \
              (rating, rating_count, five, four, three, two, one, maoyan_wanted, str(wanted))
        if better_than1 is not None:
            sql += ', better_than1="%s"' % better_than1
        if better_than2 is not None:
            sql += ', better_than2="%s"' % better_than2
        if better_than3 is not None:
            sql += ', better_than3="%s"' % better_than3
        sql += ' WHERE mid="%d"' % int(mmid)
        if not connector.execute(sql):
            print('FAILED update movies rating %d' % mmid)
    connector.close()


def update_award():
    connector = MysqlConnector()
    config = Config()
    config.read_config_src('general.ini')
    target_year = int(config.config_parser.get('General', 'target_year'))
    connector.connect()
    # Get movies which box over 1M from raw database
    sql = 'SELECT mmid FROM movies_awards GROUP BY mmid'
    movies = connector.search(sql)
    award_maps = {}
    for movie in movies:
        mmid = int(movie[0])
        sql = 'SELECT * FROM movies_awards WHERE mmid="%s"' % mmid
        item_list = connector.search(sql)
        portraits = ''
        award_detail1 = ''
        award_detail2 = ''
        for item in item_list:
            portraits += str(item[1]) + ','
            if item[1] != 'None' and item[1] is not None:
                award_detail1 = "获奖：" + item[1] + ','
            elif item[2] != 'None' and item[2] is not None:
                award_detail1 = "提名：" + item[2] + ','
                continue
            if item[2] != 'None' and item[2] is not None:
                award_detail2 = "提名：" + item[2] + ','
        portraits = portraits.rstrip(',')
        award_detail1 = award_detail1.rstrip(',')
        award_detail2 = award_detail2.rstrip(',')
        award_maps[mmid] = (portraits, award_detail1, award_detail2)
    connector.close()
    connector.connect(database='filmdom_output_%d' % target_year)
    for key in award_maps.keys():
        sql = 'UPDATE movies SET award_name="%s", award_detail1="%s", award_detail2="%s" WHERE mid="%d" AND year="%d"' % \
              (award_maps[key][0], award_maps[key][1], award_maps[key][2], int(key), int(target_year))
        connector.execute(sql)
    connector.close()


def update_participants():
    connector = MysqlConnector()
    config = Config()
    config.read_config_src('general.ini')
    target_year = int(config.config_parser.get('General', 'target_year'))
    connector.connect(database='filmdom_output_%d' % target_year)
    # Get movies which box over 1M from raw database
    sql = 'SELECT mid FROM movies WHERE year="%d"' % int(target_year)
    movies = connector.search(sql)
    connector.close()
    connector.connect()
    actors_map = {}
    for movie in movies:
        sql = 'SELECT * FROM movies_participants WHERE mmid="%d"' % int(movie[0])
        participants = connector.search(sql)
        director = ''
        director_id = ''
        actor = ''
        actor_id = ''
        actor_role = ''
        for participant in participants:
            if participant[1] == '导演':
                director += participant[2] + ','
                director_id += str(participant[4]) + ','
            else:
                actor += participant[2] + ','
                actor_id += str(participant[4]) + ','
                actor_role += participant[3].replace('饰：', '').strip() + ',' if participant[3] is not None else ''

        actors_map[int(movie[0])] = (director.rstrip(','), director_id.rstrip(','),
                                     actor.rstrip(','), actor_id.rstrip(','), actor_role.rstrip(','))
    connector.close()
    connector.connect(database='filmdom_output_%d' % target_year)
    for key in actors_map:
        sql = 'UPDATE movies SET director="%s", director_id="%s", actor="%s", actor_id="%s", actor_role="%s" WHERE mid="%d"' % \
              (actors_map[key][0], actors_map[key][1], actors_map[key][2], actors_map[key][3], actors_map[key][4], int(key))
        connector.execute(sql)
    connector.close()


def update_company():
    connector = MysqlConnector()
    config = Config()
    config.read_config_src('general.ini')
    target_year = int(config.config_parser.get('General', 'target_year'))
    connector.connect(database='filmdom_output_%d' % target_year)
    # Get movies which box over 1M from raw database
    sql = 'SELECT mid FROM movies WHERE year="%d"' % target_year
    movies = connector.search(sql)
    connector.close()
    connector.connect()
    company_map = {}
    for movie in movies:
        sql = 'SELECT * FROM movie_company_new WHERE mid="%d"' % int(movie[0])
        companies = connector.search(sql)
        company_name = ''
        company_id = ''
        company_duty = ''
        for company in companies:
            if len(company_name + company[3]) > 255:
                break
            company_name += company[3] + ','
            company_id += company[2] + ','
            company_duty += company[4] + ','
        company_name = company_name.rstrip(',')
        company_id = company_id.rstrip(',')
        company_duty = company_duty.rstrip(',')
        company_map[int(movie[0])] = (company_name, company_id, company_duty)

    connector.close()
    connector.connect(database='filmdom_output_%d' % target_year)
    for key in company_map:
        sql = 'UPDATE movies SET company_name="%s", company_id="%s", company_duty="%s" WHERE mid="%d"' % \
              (company_map[key][0], company_map[key][1], company_map[key][2], int(key))
        connector.execute(sql)
    connector.close()


def update_year_rank():
    connector = MysqlConnector()
    config = Config()
    config.read_config_src('general.ini')
    target_year = int(config.config_parser.get('General', 'target_year'))
    connector.connect(database='filmdom_output_%d' % target_year)
    # Get movies which box over 1M from raw database
    sql = 'SELECT mid, box_office FROM movies WHERE year="%d"' % target_year
    box_list = connector.search(sql)
    mid_box_pair = {}
    for item in box_list:
        mid_box_pair[item[0]] = float(item[1])
    z = zip(mid_box_pair.values(), mid_box_pair.keys())
    z = sorted(z)
    z.reverse()
    print(z)

    for item in z:
        rank = z.index(item) + 1
        sql = 'UPDATE movies SET year_rank="%d" WHERE mid="%d"' % (rank, item[1])
        connector.execute(sql)
    connector.close()


def update_all_rank():
    connector = MysqlConnector()
    config = Config()
    config.read_config_src('general.ini')
    target_year = int(config.config_parser.get('General', 'target_year'))
    connector.connect(database='filmdom_output_%d' % target_year)
    # Get movies which box over 1M from raw database
    sql = 'SELECT mid, box_office FROM movies'
    box_list = connector.search(sql)
    mid_box_pair = {}
    for item in box_list:
        mid_box_pair[item[0]] = float(item[1])
    z = zip(mid_box_pair.values(), mid_box_pair.keys())
    z = sorted(z)
    z.reverse()
    print(z)

    for item in z:
        rank = z.index(item) + 1
        sql = 'UPDATE movies SET all_rank="%d" WHERE mid="%d"' % (rank, item[1])
        connector.execute(sql)
    connector.close()


if __name__ == '__main__':
    # append_movies()
    # update_rating()
    # update_award()
    # update_participants()
    # update_company()
    # update_year_rank()
    update_all_rank()

