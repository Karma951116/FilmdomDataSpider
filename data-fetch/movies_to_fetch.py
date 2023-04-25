from NetworkHelper import NetworkHelper
from MysqlConnector import MysqlConnector
from ConfigHelper import Config

from bs4 import BeautifulSoup
import time
import random

# 猫眼影片地区代码，大陆：2，香港：10，台湾：13
sourceId = 13
# 年份代码，2022年为17，其他年份依次递增或递减
yearId = 17
year = yearId - 6 + 2011
base_url = 'https://www.maoyan.com/films?' + \
           ('sourceId=%d&' % sourceId if sourceId is not None else '') + \
           'yearId=%d&showType=3&offset=%d'
if __name__ == '__main__':
    net_helper = NetworkHelper()
    config = Config()
    config.read_config_src('general.ini')
    connector = MysqlConnector()
    connector.connect()
    header = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36',
        'Cookie': '__mta=188478359.1678930917547.1678941826753.1678946945960.21; uuid_n_v=v1; uuid=24A0ABE0BCB711EDBCBCAB7DE9BBBE745660E51F7B56473198C812EC153C462A; _lxsdk_cuid=186bae83360c8-0f8c49e77755c4-26031951-1fa400-186bae83360c8; _csrf=c29a4adcd9da248c0c95b849e9be4096061d97d5687fe9ccbc753f2ba6ff8261; _lx_utm=utm_source%3DBaidu%26utm_medium%3Dorganic; Hm_lvt_703e94591e87be68cc8da0da7cbd0be2=1678339871,1678926968,1678930917,1679014014; _lxsdk=24A0ABE0BCB711EDBCBCAB7DE9BBBE745660E51F7B56473198C812EC153C462A; Hm_lpvt_703e94591e87be68cc8da0da7cbd0be2=1679017342; __mta=188478359.1678930917547.1678946945960.1679017341953.22; _lxsdk_s=186ed08ad98-14-80d-b96%7C%7C61'
    }
    offset = int(config.config_parser.get('Fetch', 'to_fetch_offset'))
    while 1:
        url = base_url % (yearId, offset)
        try:
            response = net_helper.get(url, header=header)
        except Exception as e:
            print('Failed on offset %d, retry' % offset)
            time.sleep(random.randint(3, 7))
            continue

        if response.text.__contains__("猫眼验证中心"):
            print("请手动验证")
            time.sleep(15)
            continue
        root = BeautifulSoup(response.text, 'html.parser')
        if root.find('div', class_="no-movies") is not None:
            print("yearId:%d 已获取所有影片" % yearId)
            break

        movies = root.find_all('div', class_='movie-item-hover')
        for movie in movies:
            show_time = movie.find('div', class_='movie-hover-title movie-hover-brief')
            if not show_time.text.__contains__(str(year)):
                continue
            mmid = movie.find('a').get('data-val').split(':')[1].replace('}', '')
            name = movie.find('img', class_='movie-hover-img').get('alt')

            sql = 'INSERT IGNORE INTO movies_to_fetch_from_maoyan SET mmid="%d", name_zh="%s", base_fetched="%d", ' \
                  'box_summary_fetched="%d", box_day_fetched="%d", ratings_fetched="%d", fetch_time="%d"' \
                  % (int(mmid), name, 0, 0, 0, 0, int(time.time()))
            if connector.execute(sql):
                print("SUCCESS %s, %d" % (name, int(mmid)))
            else:
                print("FAILED %s, %d" % (name, int(mmid)))
        config.config_parser.set('Fetch', 'to_fetch_offset', str(offset))
        config.write_config_src('general.ini')
        time.sleep(random.randint(5, 15))
        offset += 30
