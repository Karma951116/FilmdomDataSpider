from NetworkHelper import NetworkHelper
from MysqlConnector import MysqlConnector


from bs4 import BeautifulSoup
import time
import random
import os

base_url = 'https://www.maoyan.com/films/celebrity/%d'

if __name__ == '__main__':
    net_helper = NetworkHelper()
    connector = MysqlConnector()
    connector.connect()
    sql = 'SELECT mpid, base_fetched, poster_fetched, awards_fetched, related_fetched ' \
          'FROM participants_to_fetch_from_maoyan ' \
          'WHERE base_fetched=0 OR poster_fetched=0 OR awards_fetched=0 OR related_fetched=0'
    participant_to_fetch = connector.search(sql)
    header = {
        'Connection': 'keep-alive',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36',
        'Cookie': '__mta=213098155.1680074654375.1680082404322.1680082406388.11; __mta=213098155.1680074654375.1680080098389.1680080107449.7; _lxsdk_cuid=18726b63b745f-0576794d787e22-26031851-1fa400-18726b63b75c8; uuid_n_v=v1; uuid=BCC077A0CE0211ED965E691062937F3CD5645179D5F24055B279BDDF40D43FF5; _lx_utm=utm_source%3DBaidu%26utm_medium%3Dorganic; _csrf=010f1b433b4618e0087c5667d2ef36e8f720000646776ff66bf61ce2c0a5cda0; Hm_lvt_703e94591e87be68cc8da0da7cbd0be2=1680074654,1680080091; _lxsdk=BCC077A0CE0211ED965E691062937F3CD5645179D5F24055B279BDDF40D43FF5; __mta=213098155.1680074654375.1680080095258.1680080098389.6; Hm_lpvt_703e94591e87be68cc8da0da7cbd0be2=1680082406; _lxsdk_s=1872cb701e1-335-6e0-de0%7C%7C5'
    }
    for participant in participant_to_fetch:
        url = base_url % participant[0]
        base_fetched = participant[1]
        poster_fetched = participant[2]
        awards_fetched = participant[3]
        related_fetched = participant[4]
        try:
            response = net_helper.get(url, header=header)
        except Exception as e:
            print('Failed: Connection Error %d' % int(participant[0]))
            continue
        if '猫眼验证' in response.text:
            print('请手动验证')
            time.sleep(random.randint(5, 15))
            continue
        root = BeautifulSoup(response.text, 'html.parser')
        if base_fetched == 0:
            name_zh = root.find('p', class_='china-name cele-name')
            name_zh = name_zh.text if name_zh is not None else None
            name_en = root.find('p', class_='eng-name cele-name')
            name_en = name_en.text if name_en is not None else None
            jobs = root.find('span', class_='profession')
            jobs = jobs.text if jobs is not None else None
            birthday = root.find('span', class_='birthday')
            birthday = birthday.text if birthday is not None else None
            born = None
            nationality = None
            sex = None
            constellation = None
            left_info = root.find('dl', class_='dl-left')
            right_info = root.find('dl', class_='dl-right')
            if left_info is not None:
                for dt in left_info.find_all('dt', class_='basicInfo-item name'):
                    if '出生地' in dt.text:
                        born = dt.find_next_sibling().text
                    if '性    别' in dt.text:
                        sex = dt.find_next_sibling().text
                    if '国    籍' in dt.text:
                        nationality = dt.find_next_sibling().text
                    if '星    座' in dt.text:
                        constellation = dt.find_next_sibling().text

            if right_info is not None:
                for dt in right_info.find_all('dt', class_='basicInfo-item name'):
                    if '星    座' in dt.text:
                        constellation = dt.find_next_sibling().text
                    if '出生地' in dt.text:
                        born = dt.find_next_sibling().text
                    if '性    别' in dt.text:
                        sex = dt.find_next_sibling().text
                    if '国    籍' in dt.text:
                        nationality = dt.find_next_sibling().text

            introdece = root.find('p', class_='cele-desc')
            introdece = introdece.text.replace('"', '\\\"') if introdece is not None else None

            sql = 'INSERT IGNORE INTO participant_base SET mpid="%d", name_zh="%s", jobs="%s"' \
                  % (int(participant[0]), name_zh, jobs)
            if name_en is not None:
                sql += ', name_en="%s"' % name_en
            if birthday is not None:
                sql += ', birthday="%s(%s)"' % (birthday, constellation)
            if born is not None:
                sql += ', born="%s"' % born
            if nationality is not None:
                sql += ', nationality="%s"' % nationality
            if sex is not None:
                sql += ', sex="%s"' % sex
            if introdece is not None:
                sql += ', introduce="%s"' % introdece

            if connector.execute(sql):
                sql = 'UPDATE participants_to_fetch_from_maoyan SET base_fetched=1, fetch_time="%d" WHERE mpid=%d' % \
                      (int(time.time()), int(participant[0]))
                connector.execute(sql)
                print('--------------------------------')
                print('SUCCESS basic %d' % int(participant[0]))
            else:
                print('FAILED basic %d' % int(participant[0]))

        if poster_fetched == 0:
            img_str = root.find('img', class_='avatar').get('src')
            poster_response = net_helper.get(img_str)
            poster_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + \
                          '\\participant_posters\\' + '%s.jpg' % participant[0]
            if poster_response.status_code == 200:
                open(poster_path, 'wb').write(poster_response.content)
            if os.path.exists(poster_path):
                sql = 'UPDATE participants_to_fetch_from_maoyan SET poster_fetched=1, fetch_time="%d" WHERE mpid=%d' % \
                      (int(time.time()), int(participant[0]))
                connector.execute(sql)
                print('SUCCESS poster %d' % int(participant[0]))
            else:
                print('FAILED poster %d' % int(participant[0]))

        if awards_fetched == 0:
            award_block = root.find('div', class_='award')
            mod_content = award_block.find('div', class_='mod-content') if award_block is not None else None
            award_slider = mod_content.find('div', class_='award-slider award-class slider') if mod_content is not None else None
            portrait_list = award_slider.findAll('div', class_='item') if award_slider is not None else None
            award_detail_block = mod_content.find('div', class_='award-detail') if mod_content is not None else None
            #award_detail = award_detail_block.findAll('div', class_='item')
            if portrait_list is None:
                sql = 'UPDATE participants_to_fetch_from_maoyan SET awards_fetched=2, fetch_time="%d" WHERE mpid=%d' % \
                      (int(time.time()), int(participant[0]))
                connector.execute(sql)
                print('SUCCESS awards no data %d' % int(participant[0]))

            if portrait_list is not None and award_detail_block is not None:
                fetched = True
                for div in portrait_list:
                    index = div.get('data-index')
                    portrait = div.find('p', class_='award-name').text
                    detail_list = award_detail_block.find('div', class_='item', attrs={'data-index': '%d' % int(index)})
                    details = detail_list.findAll('li')
                    for tag in details:
                        award = tag.find('div', class_='detail-left').text
                        if '"' in award:
                            award = award.replace('"', '\\\"')
                        detail_right_list = tag.find('div', class_='detail-right').text.split('\n')
                        detail_right_list = list(filter(None, detail_right_list))
                        film = None
                        year = None
                        role = None
                        if detail_right_list is not None and detail_right_list != []:
                            film = detail_right_list[0]
                            if '"' in film:
                                film = film.replace('"', '\\\"')
                            year = detail_right_list[1].strip()
                            role = detail_right_list[2].replace('/', '').strip()
                            if '"' in role:
                                role = role.replace('"', '\\\"')

                        sql = 'INSERT IGNORE INTO participant_award SET mpid="%d", portrait="%s", award="%s"' % \
                              (int(participant[0]), portrait, award)
                        if film is not None and film != '':
                            sql += ', film="%s"' % film
                        if year is not None and year != '':
                            sql += ', year="%d"' % int(year)
                        if role is not None and role != '':
                            sql += ', role="%s"' % role
                        if not connector.execute(sql):
                            print('FAILED awards %d' % int(participant[0]))
                            fetched = False

                if fetched:
                    sql = 'UPDATE participants_to_fetch_from_maoyan SET awards_fetched=1, fetch_time="%d" WHERE mpid=%d' % \
                          (int(time.time()), int(participant[0]))
                    connector.execute(sql)
                    print('SUCCESS awards %d' % int(participant[0]))

        if related_fetched == 0:
            class_list = ['item', 'item slick-slide slick-current slick-active', 'item slick-slide']
            fetched = True
            relation_block = root.find('div', class_='relationship')
            if relation_block is None:
                sql = 'UPDATE participants_to_fetch_from_maoyan SET related_fetched=2, fetch_time="%d" WHERE mpid=%d' % \
                      (int(time.time()), int(participant[0]))
                connector.execute(sql)
                print('SUCCESS related no data %d' % int(participant[0]))
            else:
                for item in class_list:
                    rel_item_list = relation_block.find('div', class_=item)
                    if rel_item_list is None or len(rel_item_list) == 0:
                        continue
                    for div in rel_item_list.find_all('div', class_='rel-item'):
                        rel_name_zh = div.find('p', class_='rel-name').text
                        relation = div.find('p', class_='rel-relation').text
                        rel_mpid = div.find('a').get('data-val').split(':')[1].rstrip('}')

                        sql = 'INSERT IGNORE INTO participant_related SET mpid="%d", related_name="%s", related_id="%d", ' \
                              'relation="%s"' % (int(participant[0]), rel_name_zh, int(rel_mpid), relation)
                        if not connector.execute(sql):
                            print('FAILED related %d' % int(participant[0]))
                            fetched = False
                if fetched:
                    sql = 'UPDATE participants_to_fetch_from_maoyan SET related_fetched=1, fetch_time="%d" WHERE mpid=%d' % \
                          (int(time.time()), int(participant[0]))
                    connector.execute(sql)
                    print('SUCCESS related %d' % int(participant[0]))

        #time.sleep(random.randint(5, 15))
