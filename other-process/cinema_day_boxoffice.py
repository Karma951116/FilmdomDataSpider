from MysqlConnector import MysqlConnector
from ConfigHelper import Config


def update_year_basis():
    output_connector = MysqlConnector()
    config = Config()
    config.read_config_src('general.ini')
    target_year = int(config.config_parser.get('General', 'target_year'))
    output_connector.connect(database='filmdom_output_%d' % int(target_year))
    pre_year = 2017
    cur_year = 2018
    pre_table_name = 'cinema_day_boxoffice_%d' % pre_year
    cur_table_name = 'cinema_day_boxoffice_%d' % cur_year
    sql = 'SELECT id FROM %s WHERE ISNULL(percent_boxoffice) GROUP BY id' % cur_table_name
    cinema_list = output_connector.search(sql)
    print(len(cinema_list))
    for cinema in cinema_list:
        cinema_id = int(cinema[0])
        sql = 'SELECT date, day_boxoffice, day_admission FROM %s WHERE id = "%d" AND ISNULL(percent_boxoffice)' \
              % (cur_table_name, cinema_id)
        data_list = output_connector.search(sql)
        for data in data_list:
            day = str(data[0])[5:]
            date = str(pre_year) + '-' + day
            sql = 'SELECT day_boxoffice, day_admission FROM %s WHERE id="%d" AND date="%s"' % (pre_table_name, cinema_id, date)
            pre_data = output_connector.search(sql)
            box_year_basis = 0.0
            admission_year_basis = 0.0
            try:
                cur_box = float(data[1])
                pre_box = float(pre_data[0][0])
                box_year_basis = (cur_box - pre_box) / pre_box if pre_box != 0 else 0

                cur_admission = float(data[2])
                pre_admission = float(pre_data[0][1])
                admission_year_basis = (cur_admission - pre_admission) / pre_admission if pre_admission != 0 else 0
            except Exception as e:
                print(e)

            sql = 'UPDATE %s SET percent_boxoffice="%f", percent_admission="%f" WHERE id="%d" AND date="%s"' \
                  % (cur_table_name, box_year_basis, admission_year_basis, cinema_id, data[0])
            output_connector.execute(sql)
        print('success %d' % cinema_id)
    output_connector.close()


if __name__ == '__main__':
    update_year_basis()
