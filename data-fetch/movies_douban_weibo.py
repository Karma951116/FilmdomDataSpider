from NetworkHelper import NetworkHelper
from MysqlConnector import MysqlConnector
from ConfigHelper import Config

from bs4 import BeautifulSoup
import time
import random
import execjs
import os
import re
import json

douban_url = 'https://search.douban.com/movie/subject_search?search_text=%s&cat=1002'
weibo_url = 'https://m.s.weibo.com/ajax_topic/detail?q=%s'

def douban_decrypt(response, ctx):
    search_result = re.search('window.__DATA__ = "([^"]+)"', response.text)
    if search_result is None:
        return None
    r = search_result.group(1)  # 加密的数据
    # 导入js
    data = ctx.call('decrypt', r)
    return data['payload']['items']


def get_comments(html):
    bs = BeautifulSoup(html, 'html.parser')
    section = bs.find(class_='reviews mod movie-content')
    if section is None:
        return None
    search_result = re.search(r'[\u4e00-\u9fff]+\W+\d+\W+[\u4e00-\u9fff]+', section.text)
    if search_result is not None:
        film_comment_value = None
        film_comment_num = None
        value_str = re.search(r'\d+', search_result.group(0))
        if value_str is not None:
            film_comment_value = int(value_str.group(0))
            if film_comment_value is not None and film_comment_value != '':
                film_comment_num = unit_convert(int(film_comment_value))
    short_comment_value = None
    short_comment_num = None
    comments_section = bs.find(id='comments-section')
    if comments_section is not None:
        div = comments_section.find(class_='mod-hd')
        if div is not None:
            span = div.find(class_='pl')
            if span is not None:
                a_tag = span.find('a')
                if a_tag is not None:
                    search_result = re.search(r'[\u4e00-\u9fff]+\W+\d+\W+[\u4e00-\u9fff]+', a_tag.text)
                    if search_result is not None:
                        value_str = re.search(r'\d+', search_result.group(0))
                        if value_str is not None:
                            short_comment_value = int(value_str.group(0))
                            if short_comment_value is not None and short_comment_value != '':
                                short_comment_num = unit_convert(int(short_comment_value))

    return [film_comment_value, film_comment_num, short_comment_value, short_comment_num]


def unit_convert(num):
    # 单位转换到万
    ret_num = ''
    if num < 10000:
        ret_num = str(num)
    else:
        if (num / 10000) > 10000:
            ret_num = str(num / (10000 * 10000)) + '亿'
        else:
            ret_num = str(num / 10000) + '万'
    return ret_num


def remove_unit(num, unit):
    # 单位转换到万
    ret_num = 0
    if unit == '亿':
        ret_num = num * 10000 * 10000
    elif unit == '万':
        ret_num = num * 10000
    elif unit is None or unit is '':
        ret_num = num
    return ret_num


def get_discussions_num(html_doc):
    diction = json.loads(html_doc)
    baseData = diction['data']['baseData']
    if baseData is None:
        return None
    value = baseData['m']['val']
    unit = baseData['m']['unit']
    return [str(value) + str(unit), remove_unit(value, unit)]


if __name__ == '__main__':
    net_helper = NetworkHelper()
    output_connector = MysqlConnector()
    raw_connector = MysqlConnector()
    config = Config()
    config.read_config_src('general.ini')
    target_year = int(config.config_parser.get('General', 'target_year'))
    output_connector.connect(database='filmdom_output_%d' % int(target_year))
    raw_connector.connect()
    sql = 'SELECT film_name, mid FROM movies WHERE year="%d"' % target_year
    movies = output_connector.search(sql)

    with open(os.path.dirname(os.path.dirname(os.path.abspath(__file__))) +
              '\\douban_decrypt.js', 'r', encoding='gbk') as f:
        decrypt_js = f.read()
    ctx = execjs.compile(decrypt_js)
    for movie in movies:
        film_name = movie[0]
        mmid = int(movie[1])
        url = douban_url % film_name
        try:
            response = net_helper.get(url)
        except Exception as e:
            print('Failed: Connection Error %s' % film_name)
            continue
        results = douban_decrypt(response, ctx)
        if len(results) <= 0:
            print('%s无解析数据，跳过' % film_name)
            time.sleep(5)
            continue
        info = None
        for item in results:
            if film_name in item['title'] and str(target_year) in item['title']:
                info = item
                break
        if info is None:
            print('%s 无数据' % (film_name))
            continue

        url = info['url']
        search_result = re.search(r'\d+', url)
        did = None
        if search_result is not None:
            did = search_result.group(0)
        time.sleep(5)
        header = {
            'Connection': 'keep-alive',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36',
            'Cookie': 'll="108288"; bid=Urzs3pZipk0; _pk_id.100001.4cf6=47e432d616bca980.1681192480.1.1681192480.1681192480.; _pk_ses.100001.4cf6=*; ap_v=0,6.0; __yadk_uid=WL3dxE5bFBpSi40GLnyvnrq4vMdvwXQL'
        }
        response = net_helper.get(url, header=header)
        comments_list = None
        if response.status_code == 200 or response.text is not None:
            comments_list = get_comments(response.text)

        sql = 'UPDATE movies SET did="%d", douban_num="%s", douban_value="%d" WHERE mid="%d"' \
              % (int(did) if did is not None else 'NULL',
                 comments_list[3] if comments_list is not None else 'NULL',
                 int(comments_list[2]) if comments_list is not None else 'NULL',
                 mmid)
        output_connector.execute(sql)

        url = weibo_url % film_name
        try:
            response = net_helper.get(url)
        except Exception as e:
            print('Failed: Connection Error %s' % film_name)
            continue
        discussions_num = get_discussions_num(response.text)
        if discussions_num is None:
            continue
        sql = 'UPDATE movies SET weibo_discussion="%s", weibo_value="%d" WHERE mid="%d"' \
              % (discussions_num[0], discussions_num[1], mmid)
        output_connector.execute(sql)
        time.sleep(random.randint(5, 10))
    raw_connector.close()
    output_connector.close()



