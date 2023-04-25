from NetworkHelper import NetworkHelper
from MysqlConnector import MysqlConnector

from bs4 import BeautifulSoup
import time
import random
import execjs
import os
import re

base_url = 'https://maoyan.com/films/%d'

if __name__ == '__main__':
    net_helper = NetworkHelper()
    connector = MysqlConnector()
    connector.connect()
    sql = 'SELECT mmid, base_fetched, poster_fetched, awards_fetched, participants_fetched ' \
          'FROM movies_to_fetch_from_maoyan ' \
          'WHERE base_fetched=0 OR poster_fetched=0 OR awards_fetched=0 OR participants_fetched=0'
    movies_to_fetch = connector.search(sql)
    with open(os.path.dirname(os.path.dirname(os.path.abspath(__file__))) +
              '\\maoyan_base_url_generator.js', 'r', encoding='utf-8') as f:
        generator = execjs.compile(f.read())
    header = {
        'Connection': 'keep-alive',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36',
        'Cookie': 'uuid_n_v=v1; uuid=24A0ABE0BCB711EDBCBCAB7DE9BBBE745660E51F7B56473198C812EC153C462A; _lxsdk_cuid=186bae83360c8-0f8c49e77755c4-26031951-1fa400-186bae83360c8; WEBDFPID=53u95wx422w0508xz522607844y4xw78813uw22z0yu979585yu41649-1994649710534-1679289709588WKIQOIQfd79fef3d01d5e9aadc18ccd4d0c95072951; token=AgGuIH7F2qba6g4ZAHGUSX4d_V5OW9sA2nmg-UfBPDD5597Lj6HWXTIOaSUIl96m-Qvg5XuAujozDAAAAABPFwAAEp9O8WY8h9inz3QsRE834azT4IgUeLmlvcU2brIvSexkceuJjJoTHBFVrARZGsSC; uid=1097461883; uid.sig=Qzn0f6oHqGvrFPGYvWuz1uoqSK0; _csrf=01ce4fdd7998e7af0a970f77df889e7dd5e9a8740e9301df0173d31238cb7646; Hm_lvt_703e94591e87be68cc8da0da7cbd0be2=1679014014,1679272915,1679278384,1679358096; _lx_utm=utm_source%3DBaidu%26utm_medium%3Dorganic; _lxsdk=24A0ABE0BCB711EDBCBCAB7DE9BBBE745660E51F7B56473198C812EC153C462A; __mta=188478359.1678930917547.1679378973144.1679379486522.61; Hm_lpvt_703e94591e87be68cc8da0da7cbd0be2=1679379526; _lxsdk_s=18702c97996-54b-157-ec6%7C%7C8'
    }
    for movie in movies_to_fetch:
        base_fetched = movie[1]
        poster_fetched = movie[2]
        awards_fetched = movie[3]
        participants_fetched = movie[4]
        try:
            response = net_helper.get(generator.eval('generateSign(%d)' % int(movie[0])), header=header)
        except Exception as e:
            print('Failed: Connection Error %d' % int(movie[0]))
            continue
        if response.text == '\n':
            print('请手动验证 %d' % int(movie[0]))
            time.sleep(15)
            continue
        root = BeautifulSoup(response.text, 'html.parser')
        if base_fetched == 0:
            movie_brief = root.find('div', class_='movie-brief-container')
            # basic fetch
            # chinese & english name
            name_zh = movie_brief.find('h1', class_='name').text
            name_en = movie_brief.find('div', class_='ename ellipsis').text
            # genres
            genres = ''
            for a in movie_brief.find_all('a', class_='text-link'):
                genres += a.text.strip()
                genres += ','
            genres = genres.rstrip(',')
            # show & duration country
            li_list = movie_brief.find_all('li', class_='ellipsis')
            product_country = None
            show_country = None
            duration = None
            release_date = None
            for li in li_list:
                if re.search(r'\S+\s+[/]\s+\d+\S+', li.text) is not None:
                    product_country = li.text.split('/')[0].strip()
                    duration = li.text.split('/')[1].strip()
                if re.search(r'\d{4}-\d{2}-\d{2}[ \d{2}:\d{2}]?\S+', li.text) is not None:
                    #release_date = re.search(r'\d{4}-\d{2}-\d{2}', li.text).string.replace('-', '/').strip()
                    release_date = re.search(r'\d{4}-\d{2}-\d{2}', li.text).group().replace('-', '/').strip()
                    show_country = re.search(r'[\u4e00-\u9fa5]+', li.text).group()
            sql = 'INSERT IGNORE INTO movies_base SET mmid="%d", name_zh="%s", name_en="%s", release_date="%s", duration="%s", ' \
                  'show_country="%s", genre="%s", product_country="%s"' % \
                  (int(movie[0]), name_zh, name_en, release_date, duration, show_country, genres, product_country)
            if connector.execute(sql):
                sql = 'UPDATE movies_to_fetch_from_maoyan SET base_fetched=1, fetch_time="%d" WHERE mmid=%d' % \
                      (int(time.time()), int(movie[0]))
                connector.execute(sql)
                print('--------------------------------')
                print('SUCCESS basic %d' % int(movie[0]))
            else:
                print('FAILED basic %d' % int(movie[0]))
        if poster_fetched == 0:
            # poster fetch
            img_str = root.find('img', class_='avatar').get('src')
            poster_response = net_helper.get(img_str)
            poster_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + \
                          '\\movie_posters\\' + '%s.jpg' % movie[0]
            if poster_response.status_code == 200:
                open(poster_path, 'wb').write(poster_response.content)
            if os.path.exists(poster_path):
                sql = 'UPDATE movies_to_fetch_from_maoyan SET poster_fetched=1, fetch_time="%d" WHERE mmid=%d' % \
                      (int(time.time()), int(movie[0]))
                connector.execute(sql)
                print('SUCCESS poster %d' % int(movie[0]))
            else:
                print('FAILED poster %d' % int(movie[0]))

        if participants_fetched == 0:
            # participants fetch
            fetched = True
            celebrity_container = root.find('div', class_='celebrity-container clearfix')
            if celebrity_container is None:
                sql = 'UPDATE movies_to_fetch_from_maoyan SET participants_fetched=2, fetch_time="%d" WHERE mmid=%d' % \
                      (int(time.time()), int(movie[0]))
                connector.execute(sql)
                print('SUCCESS participants %d' % int(movie[0]))
            else:
                celebrity_groups = celebrity_container.find_all('div', class_='celebrity-group')
                for group in celebrity_groups:
                    participant_type = group.find('div', class_='celebrity-type').text.strip()
                    if participant_type == '导演':
                        participant_list = group.find_all('li', class_='celebrity')
                    else:
                        participant_list = group.find_all('li', class_='celebrity actor')
                    for participant in participant_list:
                        participant_name = participant.find('a', class_='name').text.strip()
                        mpid = participant.find('a', class_='name').get('href').split('/')[-1]
                        participant_role = None
                        if participant_type == '演员':
                            participant_role = participant.find('span', class_='role')
                            if participant_role is not None:
                                participant_role = participant_role.text
                                participant_role = participant_role.replace('\"', '\\"')
                        sql = 'INSERT IGNORE INTO movies_participants SET mmid="%d", type="%s", name="%s", mpid="%d"' % \
                              (int(movie[0]), participant_type, participant_name, int(mpid))
                        if participant_role is not None:
                            sql += ', role="%s"' % participant_role
                        if not connector.execute(sql):
                            print('FAILED participants %d' % int(movie[0]))
                            fetched = False
                if fetched:
                    sql = 'UPDATE movies_to_fetch_from_maoyan SET participants_fetched=1, fetch_time="%d" WHERE mmid=%d' % \
                          (int(time.time()), int(movie[0]))
                    connector.execute(sql)
                    print('SUCCESS participants %d' % int(movie[0]))


        if awards_fetched == 0:
            # awards fetch
            fetched = True
            tab_award = root.find('div', class_='tab-award tab-content')
            award_items = tab_award.find_all('li')
            for item in award_items:
                portrait = item.find('div', class_='portrait').parent.text.strip()
                div_content = item.find('div', class_='content')
                award = None
                nominate = None
                for div in div_content.find_all('div'):
                    if '获奖' in div.text:
                        award = div.text.split('：')[1].strip()
                    elif '提名' in div.text:
                        nominate = div.text.split('：')[1].strip()
                sql = 'INSERT IGNORE INTO movies_awards SET mmid="%d", portrait="%s"' % \
                      (int(movie[0]), portrait)
                if award is not None:
                    sql += ', award="%s"' % award
                if nominate is not None:
                    sql += ', nominate="%s"' % nominate
                if not connector.execute(sql):
                    print('FAILED awards %d' % int(movie[0]))
                    fetched = False
            if fetched:
                sql = 'UPDATE movies_to_fetch_from_maoyan SET awards_fetched=1, fetch_time="%d" WHERE mmid=%d' % \
                      (int(time.time()), int(movie[0]))
                connector.execute(sql)
                print('SUCCESS awards %d' % int(movie[0]))
                print('------------------------------')
        time.sleep(random.randint(5, 15))
    connector.close()