from MysqlConnector import MysqlConnector
from ConfigHelper import Config


# main-process order : 2
def cid_match():
    connector = MysqlConnector()
    config = Config()
    config.read_config_src('general.ini')
    target_year = config.config_parser.get('General', 'target_year')
    connector.connect()
    sql = 'SELECT company_name_zh FROM movie_company_new WHERE cid="" GROUP BY company_name_zh'
    companies = connector.search(sql)
    connector.close()
    name_id_pair = {}
    connector.connect(database='filmdom_output_%d' % int(target_year))
    for company in companies:
        sql = 'SELECT id FROM company_basic WHERE name="%s"' % company[0].strip()
        cid = connector.search(sql)
        if len(cid) > 0:
            name_id_pair[company[0].strip()] = cid[0][0]
    connector.close()
    connector.connect()
    for key in name_id_pair.keys():
        sql = 'UPDATE movie_company_new SET cid="%d" WHERE company_name_zh="%s"' % (name_id_pair[key], key)
        connector.execute(sql)
    connector.close()


# main-process order : 5
def append():
    connector = MysqlConnector()
    config = Config()
    config.read_config_src('general.ini')
    target_year = int(config.config_parser.get('General', 'target_year'))
    connector.connect()
    sql = 'SELECT * FROM movie_company_new'
    movie_company_new = connector.search(sql)
    connector.close()
    connector.connect(database='filmdom_output_%d' % int(target_year))
    for item in movie_company_new:
        mmid = int(item[0])
        movie_name = item[1]
        cid = int(item[2])
        company_name = item[3]
        field = item[4]
        try:
            sql = 'SELECT film_id, box_office FROM movies WHERE mid="%d"' % mmid
            movie_info = connector.search(sql)
            film_id = int(movie_info[0][0])
            boxoffice = movie_info[0][1]
            sql = 'SELECT company_lng, company_lat FROM company_basic WHERE id="%d"' % cid
            company_info = connector.search(sql)
            company_lng = company_info[0][0]
            company_lat = company_info[0][1]
        except Exception as e:
            print(movie_name)
        sql = 'INSERT IGNORE INTO movie_company SET company_name="%s", company_id="%d", film_name="%s", film_id="%d", ' \
              'mid="%d", year="%d", company_duty="%s", company_lng="%s", company_lat="%s", box_office="%s"' % \
              (company_name, cid, movie_name, film_id, mmid, target_year, field, company_lng, company_lat, boxoffice)
        connector.execute(sql)
    connector.close()


if __name__ == '__main__':
    #cid_match()
    append()
