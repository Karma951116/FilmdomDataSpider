from NetworkHelper import NetworkHelper
from MysqlConnector import MysqlConnector
from utils import unit_convert

from bs4 import BeautifulSoup
import time
import re
import json
import random

base_url = 'http://piaofang.maoyan.com/movie/%d/audienceRating'

if __name__ == '__main__':
    net_helper = NetworkHelper()
    connector = MysqlConnector()
    connector.connect()
    sql = 'SELECT mmid, ratings_fetched ' \
          'FROM movies_to_fetch_from_maoyan ' \
          'WHERE ratings_fetched=0'
    movies_to_fetch = connector.search(sql)
    header = {
        'Connection': 'keep-alive',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36',
        'Cookie': 'uuid_n_v=v1; uuid=24A0ABE0BCB711EDBCBCAB7DE9BBBE745660E51F7B56473198C812EC153C462A; _lxsdk_cuid=186bae83360c8-0f8c49e77755c4-26031951-1fa400-186bae83360c8; WEBDFPID=53u95wx422w0508xz522607844y4xw78813uw22z0yu979585yu41649-1994649710534-1679289709588WKIQOIQfd79fef3d01d5e9aadc18ccd4d0c95072951; token=AgGuIH7F2qba6g4ZAHGUSX4d_V5OW9sA2nmg-UfBPDD5597Lj6HWXTIOaSUIl96m-Qvg5XuAujozDAAAAABPFwAAEp9O8WY8h9inz3QsRE834azT4IgUeLmlvcU2brIvSexkceuJjJoTHBFVrARZGsSC; uid=1097461883; uid.sig=Qzn0f6oHqGvrFPGYvWuz1uoqSK0; _csrf=01ce4fdd7998e7af0a970f77df889e7dd5e9a8740e9301df0173d31238cb7646; Hm_lvt_703e94591e87be68cc8da0da7cbd0be2=1679014014,1679272915,1679278384,1679358096; _lx_utm=utm_source%3DBaidu%26utm_medium%3Dorganic; _lxsdk=24A0ABE0BCB711EDBCBCAB7DE9BBBE745660E51F7B56473198C812EC153C462A; __mta=188478359.1678930917547.1679378973144.1679379486522.61; Hm_lpvt_703e94591e87be68cc8da0da7cbd0be2=1679379526; _lxsdk_s=18702c97996-54b-157-ec6%7C%7C8'
    }
    for movie in movies_to_fetch:
        url = base_url % movie[0]
        try:
            response = net_helper.get(url, header=header)
        except Exception as e:
            print('Failed: Connection Error %d' % int(movie[0]))
            continue
        root = BeautifulSoup(response.text, 'html.parser')
        # Get data json
        scripts = root.find_all('script')
        target = None
        for script in scripts:
            if 'AppData' in script.text:
                target = script
                break
        if target is None:
            print('Failed: No Data  %d' % int(movie[0]))
            continue
        json_str = target.text.replace('var AppData = ', '')
        json_str = json_str.replace('  var isProduct = true;', '')
        json_str = json_str.strip().rstrip(';')

        result = None
        try:
            result = json.loads(json_str)
        except Exception as e:
            print('Json Transform Error')
            time.sleep(random.randint(5, 15))
            continue
        comparison_list = None
        try:
            comparison_list = result['pageData']['basicInfo']['comparison']
        except Exception as e:
            print('No Comparison data')
        comparison = ''
        if comparison_list is not None:
            for item in comparison_list:
                comparison += item
                comparison += ';'
            comparison.rstrip(';')

        rating = None
        rating_count = None
        try:
            rating = result['pageData']['basicInfo']['maoyanScore']
            rating_count_str = result['pageData']['basicInfo']['commentNum']
            unit = re.search(r'[\u4e00-\u9fa5]', rating_count_str).group()
            number = rating_count_str.replace(unit, '')
            rating_count = unit_convert(number, unit)
        except Exception as e:
            print('No rating data')

        lv_2 = None
        lv_4 = None
        lv_6 = None
        lv_8 = None
        lv_10 = None
        try:
            score_list = result['pageData']['scoreDist']
            for score in score_list:
                if score['type'] == '9-10分':
                    lv_10 = '%s' % round(float(score['value'] * 100), 2) + '%'
                elif score['type'] == '7-8分':
                    lv_8 = '%s' % round(float(score['value'] * 100), 2) + '%'
                elif score['type'] == '5-6分':
                    lv_6 = '%s' % round(float(score['value'] * 100), 2) + '%'
                elif score['type'] == '3-4分':
                    lv_4 = '%s' % round(float(score['value'] * 100), 2) + '%'
                elif score['type'] == '1-2分':
                    lv_2 = '%s' % round(float(score['value'] * 100), 2) + '%'
        except Exception as e:
            print('No score data')

        sql = 'INSERT IGNORE INTO movies_ratings SET mmid="%d"' % movie[0]
        if rating is not None:
            sql += ', rating="%s"' % rating
        if rating_count is not None:
            sql += ', rating_count="%d"' % int(rating_count)
        if comparison != '':
            sql += ', comparison="%s"' % comparison
        if lv_10 is not None:
            sql += ', five_star_rate="%s"' % lv_10
        if lv_8 is not None:
            sql += ', four_star_rate="%s"' % lv_8
        if lv_6 is not None:
            sql += ', three_star_rate="%s"' % lv_6
        if lv_4 is not None:
            sql += ', two_star_rate="%s"' % lv_4
        if lv_2 is not None:
            sql += ', one_star_rate="%s"' % lv_2

        if rating is None and rating_count is None and comparison == '' and lv_10 is None and lv_8 is None and lv_6 is None and lv_4 is None and lv_2 is None:
            sql = 'UPDATE movies_to_fetch_from_maoyan SET ratings_fetched=2, fetch_time="%d" WHERE mmid=%d' % \
                  (int(time.time()), int(movie[0]))
            connector.execute(sql)
            print('SUCCESS ratings %d' % int(movie[0]))
            time.sleep(random.randint(5, 15))
            continue
        if connector.execute(sql):
            sql = 'UPDATE movies_to_fetch_from_maoyan SET ratings_fetched=1, fetch_time="%d" WHERE mmid=%d' % \
                  (int(time.time()), int(movie[0]))
            connector.execute(sql)
            print('SUCCESS ratings %d' % int(movie[0]))
        else:
            print('FAILED ratings %d' % int(movie[0]))

        time.sleep(random.randint(5, 15))
