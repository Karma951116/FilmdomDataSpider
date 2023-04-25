from MysqlConnector import MysqlConnector
from ConfigHelper import Config
from chinese_province_city_area_mapper.transformer import CPCATransformer

field_9to4 = {
	"其他技术支持": "视觉特效",
	"动画制作": "3D/动画制作",
	"后期制作": "视觉特效",
	"数字中间片": "视觉特效",
	"立体制作": "3D/动画制作",
	"视觉特效": "视觉特效",
	"声音制作": "声音/字幕",
	"数字母版": "母版制作",
	"译制": "声音/字幕"
}


def append():
    raw_connector = MysqlConnector()
    output_connector = MysqlConnector()
    config = Config()
    config.read_config_src('general.ini')
    target_year = int(config.config_parser.get('General', 'target_year'))
    output_connector.connect(database='filmdom_output_%d' % target_year)
    raw_connector.connect()
    sql = 'SELECT company_id, company_name, company_duty FROM movie_company WHERE year = %d GROUP BY company_id, company_duty' % target_year
    companies = output_connector.search(sql)
    cpca = CPCATransformer()
    for company in companies:
        cid = int(company[0])
        name = company[1]
        field = company[2]

        sql = 'select location from company_basic where id="%d" limit 1' % cid
        location = output_connector.search(sql)[0][0]
        prov = None
        city = None
        area = None
        if location is not None and location != '' and location != "None":
            location_list = [location]
            prov_city_dateframe = cpca.transform(location_list)
            prov = prov_city_dateframe.iat[0, 0]
            city = prov_city_dateframe.iat[0, 1]
            area = prov_city_dateframe.iat[0, 2]
            print(prov, city, area, location)

        four_field = field_9to4.get(field.strip())
        sql = 'select box_office from movie_company where company_id = %d and company_duty = "%s" and year = %d' % \
               (cid, field, target_year)
        box_list = output_connector.search(sql)
        film_num = len(box_list)
        box_office = 0
        for box in box_list:
            box_office += float(box[0])
        # 链接地址
        link_addr = 'http://192.168.100.72/company/%d/' % cid
        sql = 'insert into 制作公司_数据统计 (年份, 省份, 各线城市, 公司职能, 公司名称, 参与影片数量, 票房数量, 链接地址) ' \
               'values(%d, "%s", "%s", "%s", "%s", %d, %f, "%s")' \
               % (target_year, prov, city, four_field, name, film_num, box_office, link_addr)
        output_connector.execute(sql)
    raw_connector.close()
    output_connector.close()


def update_lng_lat():
    raw_connector = MysqlConnector()
    output_connector = MysqlConnector()
    config = Config()
    config.read_config_src('general.ini')
    target_year = int(config.config_parser.get('General', 'target_year'))
    raw_connector.connect()
    sql = 'SELECT * FROM province_lng_lat'
    prov_lng_lat_list = raw_connector.search(sql)
    prov_lng_lat_map = {}
    for item in prov_lng_lat_list:
        prov_lng_lat_map[item[0]] = (item[1], item[2])
    raw_connector.close()
    output_connector.connect(database='filmdom_output_%d' % target_year)
    search_sql = 'select 省份 from 制作公司_数据统计 Group By 省份'
    prov_list = output_connector.search(search_sql)
    for prov_tuple in prov_list:
        prov = prov_tuple[0]
        if prov is None or prov == '' or prov == 'None':
            continue
        lng_lat = prov_lng_lat_map[prov]
        sql = 'update 制作公司_数据统计 set 省份_经度="%s", 省份_纬度="%s" where 省份="%s"' % (
            lng_lat[0], lng_lat[1], prov)
        output_connector.execute(sql)
    raw_connector.close()
    output_connector.close()


def update_city_level():
    raw_connector = MysqlConnector()
    output_connector = MysqlConnector()
    config = Config()
    config.read_config_src('general.ini')
    target_year = int(config.config_parser.get('General', 'target_year'))
    raw_connector.connect()
    sql = 'SELECT city, level FROM city_level'

    output_connector.connect(database='filmdom_output_%d' % target_year)
    city_level_list = raw_connector.search(sql)
    city_level_dict = {}
    for city_tuple in city_level_list:
        city_level_dict[city_tuple[0]] = city_tuple[1]

    search_sql = 'select 各线城市 from 制作公司_数据统计 Group By 各线城市'
    city_list = output_connector.search(search_sql)
    for city in city_list:
        if city[0] is None or city[0] == '' or city[0] == 'None' or '线城市' in city[0] or '香港/台湾地区' in city[0]:
            continue
        level = city_level_dict[city[0]]
        sql = 'update 制作公司_数据统计 set 各线城市 = "%s" where 各线城市="%s"' % (level, city[0])
        output_connector.execute(sql)
    raw_connector.close()
    output_connector.close()


def update_shortname():
    output_connector = MysqlConnector()
    config = Config()
    config.read_config_src('general.ini')
    target_year = int(config.config_parser.get('General', 'target_year'))
    output_connector.connect(database='filmdom_output_%d' % target_year)
    sql = 'select 公司名称, 公司简称 from 制作公司_数据统计 where !ISNULL(公司简称) Group By 公司名称, 公司简称'
    company_short_list = output_connector.search(sql)
    for company in company_short_list:
        update_sql = 'update 制作公司_数据统计 set 公司简称="%s" where 公司名称="%s"' % (company[1], company[0])
        output_connector.execute(update_sql)
    output_connector.close()


def prov_city_supplement():
    output_connector = MysqlConnector()
    config = Config()
    config.read_config_src('general.ini')
    target_year = int(config.config_parser.get('General', 'target_year'))
    output_connector.connect(database='filmdom_output_%d' % target_year)
    search_sql = 'select 公司名称 from 制作公司_数据统计 where 省份="" or 各线城市="" Group By 公司名称'
    company_list = output_connector.search(search_sql)
    for company in company_list:
        company_name = company[0]
        search_sql = 'select location from company_basic where name = "%s" limit 1' % company_name
        location_list = output_connector.search(search_sql)
        try:
            location = location_list[0][0]
        except Exception as e:
            print(location)
        if location is None:
            continue
        if '香港' in location:
            prov = '香港特别行政区'
            city = '香港/台湾地区'
        elif '台北' in location or '台湾' in location:
            prov = '台湾省'
            city = '香港/台湾地区'
        elif '苏州' in location:
            prov = '浙江省'
            city = '苏州市'
        elif '霍尔果斯' in location:
            prov = '新疆维吾尔自治区'
            city = '五线城市'
        else:
            prov = input('input province for this addr')
            city = input('input city for this addr')
        update_sql = 'update 制作公司_数据统计 set 省份="%s", 各线城市="%s" where 公司名称="%s"' % \
                     (prov, city, company_name)
        output_connector.execute(update_sql)
    output_connector.close()


if __name__ == '__main__':
    # append()
    # update_lng_lat()
    # update_city_level()
    # update_shortname()
    prov_city_supplement()