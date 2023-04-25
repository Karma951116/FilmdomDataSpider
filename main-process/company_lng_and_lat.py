from MysqlConnector import MysqlConnector
from ConfigHelper import Config


def insert():
    connector = MysqlConnector()
    config = Config()
    config.read_config_src('general.ini')
    target_year = int(config.config_parser.get('General', 'target_year'))
    connector.connect(database='filmdom_output_%d' % target_year)
    sql = 'SELECT id, name, company_lng, company_lat FROM company_basic GROUP BY name, company_lng, company_lat'
    ret = connector.search(sql)
    for item in ret:
        cid = int(item[0])
        name = item[1]
        lng = item[2]
        lat = item[3]
        url = 'http://192.168.100.72/company/%d/' % cid
        sql = 'INSERT IGNORE INTO 制作公司_散点经纬度 SET 公司名称="%s", 公司经度="%s", 公司纬度="%s", 链接地址="%s"' \
              % (name, lng, lat, url)
        connector.execute(sql)

    sql = 'UPDATE 制作公司_散点经纬度 SET 公司经度=NULL WHERE 公司经度=0'
    connector.execute(sql)
    sql = 'UPDATE 制作公司_散点经纬度 SET 公司纬度=NULL WHERE 公司纬度=0'
    connector.execute(sql)
    connector.close()


if __name__ == '__main__':
    insert()
