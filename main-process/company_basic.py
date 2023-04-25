from MysqlConnector import MysqlConnector
from ConfigHelper import Config


# main-process order : 1
def add_new():
    '''
    用于追加新公司数据到company_basic，不计算排名
    :return:
    '''
    connector = MysqlConnector()
    config = Config()
    config.read_config_src('general.ini')
    target_year = int(config.config_parser.get('General', 'target_year'))
    # Get max company number
    connector.connect(database='filmdom_output_%d' % target_year)
    sql = 'SELECT MAX(id) FROM company_basic'
    max_id = connector.search(sql)
    max_id = int(max_id[0][0])
    connector.close()
    # Load new data
    connector.connect()
    sql = 'SELECT * FROM company_new'
    companies = connector.search(sql)
    connector.close()
    company_map = {}
    for company in companies:
        max_id = max_id + 1
        company_id = max_id
        name_zh = company[0]
        address = company[1]
        longitude = company[2]
        latitude = company[3]
        field = company[4]
        field = field.replace('，', ',')
        company_map[company_id] = (name_zh, address, longitude, latitude, field)

    connector.connect(database='filmdom_output_%d' % target_year)
    for key in company_map:
        sql = 'INSERT IGNORE INTO company_basic SET id="%d", name="%s", location="%s", company_lng="%s", ' \
              'company_lat="%s", field="%s"' \
              % (int(key), company_map[key][0], company_map[key][1],
                 company_map[key][2], company_map[key][3], company_map[key][4])
        if connector.execute(sql):
            print('SUCCESS insert company %d, %s' % (int(key), company_map[key][0]))
        else:
            print('FAILED insert company %d, %s' % (int(key), company_map[key][0]))
    connector.close()


def cal_movie_box_rank():
    connector = MysqlConnector()
    config = Config()
    config.read_config_src('general.ini')
    target_year = int(config.config_parser.get('General', 'target_year'))
    connector.connect(database='filmdom_output_%d' % target_year)
    sql = 'SELECT id FROM company_basic'
    companies = connector.search(sql)
    film_count_rank = {}
    box_rank = {}
    for company in companies:
        cid = company[0]
        sql = 'SELECT box_office FROM movie_company WHERE company_id="%d" GROUP BY company_id, film_id' % cid
        box_list = connector.search(sql)
        film_count = len(box_list)
        box_office = 0
        for box in box_list:
            box_office += float(box[0])
        if cid not in film_count_rank:
            film_count_rank[cid] = film_count
        if cid not in box_rank:
            box_rank[cid] = box_office
    film_count_rank = sorted(film_count_rank.items(), key=lambda x: x[1], reverse=True)
    box_rank = sorted(box_rank.items(), key=lambda x: x[1], reverse=True)
    film_count_rank = add_rank(film_count_rank)
    box_rank = add_rank(box_rank)
    for item in film_count_rank:
        sql = 'UPDATE company_basic SET num_rank="%d" WHERE id="%d"' % (int(item[2]), int(item[0]))
        connector.execute(sql)
    for item in box_rank:
        sql = 'UPDATE company_basic SET boxoffice_rank="%d" WHERE id="%d"' % (int(item[2]), int(item[0]))
        connector.execute(sql)
    connector.close()


def cal_field_rank():
    connector = MysqlConnector()
    config = Config()
    config.read_config_src('general.ini')
    target_year = int(config.config_parser.get('General', 'target_year'))
    connector.connect(database='filmdom_output_%d' % target_year)
    sql = 'SELECT id, field FROM company_basic'
    companies = connector.search(sql)
    field_refer = ['数字中间片', '声音制作', '视觉特效', '其他技术支持', '动画制作', '后期制作', '译制', '数字母版', '立体制作']
    field_rank = {}
    for field in field_refer:
        if field not in field_rank:
            field_rank[field] = {}
        for company in companies:
            if field in company[1]:
                cid = int(company[0])
                sql = 'SELECT box_office FROM movie_company WHERE company_id="%d" and FIND_IN_SET("%s", company_duty)' \
                      % (cid, field)
                boxes = connector.search(sql)
                company_field_box = 0
                for box in boxes:
                    company_field_box += float(box[0])
                field_rank[field][cid] = company_field_box
    for key in field_rank.keys():
        field_rank[key] = sorted(field_rank[key].items(), key=lambda x: x[1], reverse=True)
        field_rank[key] = add_rank(field_rank[key])
    for company in companies:
        cid = int(company[0])
        fields = company[1].split(',')
        rank_str = ''
        for field in fields:
            for tup in field_rank[field]:
                if int(tup[0]) == cid:
                    rank_str += str(tup[2]) + ','
        rank_str = rank_str.rstrip(',')
        sql = 'UPDATE company_basic SET filed_rank = "%s" WHERE id = %d' % (rank_str, cid)
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
    # add_new()
    # cal_movie_box_rank()
    cal_field_rank()
