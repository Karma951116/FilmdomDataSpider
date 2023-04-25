from NetworkHelper import NetworkHelper
from MysqlConnector import MysqlConnector
from utils import unit_convert

from bs4 import BeautifulSoup
import time
import json
import random


base_url = 'https://piaofang.maoyan.com/i/api/movie/getBoxShow?movieId=%d&boxLevel=1'
if __name__ == '__main__':
    net_helper = NetworkHelper()
    connector = MysqlConnector()
    connector.connect()
    sql = 'SELECT mmid, box_summary_fetched, box_day_fetched FROM movies_to_fetch_from_maoyan ' \
          'WHERE box_summary_fetched=0 OR box_day_fetched=0'
    movies_to_fetch_box = connector.search(sql)
    if len(movies_to_fetch_box) == 0:
        print('Data all fetched')
    for movie in movies_to_fetch_box:
        url = base_url % movie[0]
        summary_fetched = movie[1]
        box_fetched = movie[2]
        header = {
            'Connection': 'keep-alive',
            'Host': 'piaofang.maoyan.com',
            'Referer': 'https://piaofang.maoyan.com/i/imovie/%d/box' % int(movie[0]),
            'uid': '3789413c06569cd1fa32f13fec6f4d7ee64b9032',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36',
            'Cookie': '_lxsdk_cuid=186bae83360c8-0f8c49e77755c4-26031951-1fa400-186bae83360c8; uuid=186bae83360c8-0f8c49e77755c4-26031951-1fa400-186bae83360c8; isBoxPageUsed=true; Hm_lvt_703e94591e87be68cc8da0da7cbd0be2=1678930917,1679014014,1679272915,1679278384; Hm_lpvt_703e94591e87be68cc8da0da7cbd0be2=1679279023; _lxsdk=186bae83360c8-0f8c49e77755c4-26031951-1fa400-186bae83360c8; _lx_utm=utm_source%3DBaidu%26utm_medium%3Dorganic; _lxsdk_s=186fccaa34e-17e-c08-bf%7C%7C18'
        }
        try:
            response = net_helper.get(url=url, header=header)
        except Exception as e:
            print('Failed: Connection Error %d' % int(movie[0]))
            continue
        data = json.loads(response.text)
        if data is None:
            print('Get box failed %d' % int(movie[0]))
            continue
        if 'error' in data:
            print('No box data %d' % int(movie[0]))
            sql = 'UPDATE movies_to_fetch_from_maoyan SET box_summary_fetched=2, box_day_fetched=2, fetch_time="%d" WHERE mmid=%d' \
                  % (int(time.time()), int(movie[0]))
            connector.execute(sql)
            time.sleep(random.randint(3, 6))
            continue
        # Get summary info
        if int(summary_fetched) == 0:
            try:
                summary_list = data['data']['boxInfoDataRes'][0]['boxSummaryList']
            except IndexError as e:
                print('No summary data %d' % int(movie[0]))
                sql = 'UPDATE movies_to_fetch_from_maoyan SET box_summary_fetched=2, box_day_fetched=2, fetch_time="%d" WHERE mmid=%d' \
                      % (int(time.time()), int(movie[0]))
                connector.execute(sql)
                time.sleep(random.randint(3, 6))
                continue
            if len(summary_list) <= 0:
                print('No box data %d' % int(movie[0]))
                continue
            box_total = None
            box_first_day = None
            box_first_week = None
            for item in summary_list:
                if item['title'] == '累计综合票房':
                    box_total = unit_convert(item['valueDesc'],
                                             item['unitDesc'] if 'unitDesc' in item else None)
                elif item['title'] == '首日综合票房':
                    box_first_day = unit_convert(item['valueDesc'],
                                                 item['unitDesc'] if 'unitDesc' in item else None)
                elif item['title'] == '首周综合票房':
                    box_first_week = unit_convert(item['valueDesc'],
                                                  item['unitDesc'] if 'unitDesc' in item else None)
            sql = 'INSERT INTO movies_box_summary SET mmid="%d"' % int(movie[0])
            if box_total is not None and box_total != '--':
                sql += ', box_office="%s"' % str(box_total)
            if box_first_day is not None and box_first_day != '--':
                sql += ', box_first_day="%s"' % str(box_first_day)
            if box_first_week is not None and box_first_week != '--':
                sql += ', box_first_week="%s"' % str(box_first_week)
            # sql += ' WHERE NOT EXIST(SELECT mmid FROM movies_box_summary WHERE mmid="%d")' % int(movie[0])
            if connector.execute(sql):
                sql = 'UPDATE movies_to_fetch_from_maoyan SET box_summary_fetched=1, fetch_time="%d" WHERE mmid=%d' % \
                      (int(time.time()), int(movie[0]))
                connector.execute(sql)
                print("SUCCESS summary %d" % int(movie[0]))
            else:
                print("FAILED summary %d" % int(movie[0]))

        # Get day info
        if int(box_fetched) == 0:
            perfect = True
            day_list = data['data']['boxShowData'][0]
            for day in day_list:
                box_date = str(day['showDate'])
                box = str(day['box'])
                avg_view = day['avgShowViewDesc']
                show_count = str(day['showCount'])
                sql = 'INSERT IGNORE INTO movies_box_day SET mmid="%d", box_date="%s", box_office="%s", avg_view="%s", show_count="%s"' \
                      % (int(movie[0]), box_date, box, avg_view, show_count)
                if not connector.execute(sql):
                    print("FAILED day %d" % int(movie[0]))
                    perfect = False
            if perfect:
                sql = 'UPDATE movies_to_fetch_from_maoyan SET box_day_fetched=1, fetch_time="%d" WHERE mmid=%d' \
                      % (int(time.time()), int(movie[0]))
                connector.execute(sql)
                print("SUCCESS day %d" % int(movie[0]))
        time.sleep(random.randint(5, 15))
    connector.close()
