from MysqlConnector import MysqlConnector
from ConfigHelper import Config
import datetime


def append():
    raw_connector = MysqlConnector()
    output_connector = MysqlConnector()
    config = Config()
    config.read_config_src('general.ini')
    target_year = int(config.config_parser.get('General', 'target_year'))
    output_connector.connect(database='filmdom_output_%d' % target_year)
    raw_connector.connect()
    days = get_days_of_year(target_year)
    for day in days:
        date = day[0]
        week_of_year = day[1]
        day_of_week = day[2]
        sql = 'SELECT SUM(box_office) FROM movies_box_day WHERE box_date="%s"' % date
        box = float(raw_connector.search(sql)[0][0])
        sql = 'INSERT IGNORE INTO 总览_影片统计_周和日 SET 年份="%d", 年月日="%s", 票房数量="%f", 年中第几周="%d", 周中第几日="%d"' \
              % (target_year, date, box, week_of_year, day_of_week)
        output_connector.execute(sql)
    raw_connector.close()
    output_connector.close()


def get_days_of_year(year):
    begein = datetime.date(year, 1, 1)
    now = begein
    end = datetime.date(year, 12, 31)
    delta = datetime.timedelta(days=1)
    days = []
    while now <= end:
        week_of_year = int(now.strftime("%W")) + 1
        day_of_week = int(now.strftime("%w"))
        day_of_week = 7 if day_of_week == 0 else day_of_week
        date = now.strftime("%Y-%m-%d")
        days.append((date, week_of_year, day_of_week))
        now += delta
    return days


if __name__ == '__main__':
    append()
