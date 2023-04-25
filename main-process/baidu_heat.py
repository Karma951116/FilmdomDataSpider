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
    sql = 'SELECT * FROM participant_baidu_heat'
    ret = raw_connector.search(sql)
    for item in ret:
        mpid = int(item[0])
        name = item[1]
        province_rate = item[2]
        age_rate = item[3]
        gender_rate = item[4]
        sql = 'INSERT IGNORE INTO baidu_heat SET actors="%s", ID="%d", year="%d", province_rate="%s", ' \
              'age="%s", sex_account="%s"' % (name, mpid, target_year, province_rate, age_rate, gender_rate)
        output_connector.execute(sql)
    output_connector.close()
    raw_connector.close()


if __name__ == '__main__':
    append()

