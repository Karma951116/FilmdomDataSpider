from NetworkHelper import NetworkHelper
from MysqlConnector import MysqlConnector


from bs4 import BeautifulSoup
import time
import random

base_url = 'http://piaofang.maoyan.com/movie/%d/wantindex'

if __name__ == '__main__':
    net_helper = NetworkHelper()
    connector = MysqlConnector()
    connector.connect()
    sql = 'SELECT mmid, wanted_fetched ' \
          'FROM movies_to_fetch_from_maoyan ' \
          'WHERE wanted_fetched=0'
    movies_to_fetch = connector.search(sql)
    header = {
        'Connection': 'keep-alive',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36',
        'Cookie': 'uuid_n_v=v1; uuid=24A0ABE0BCB711EDBCBCAB7DE9BBBE745660E51F7B56473198C812EC153C462A; _lxsdk_cuid=186bae83360c8-0f8c49e77755c4-26031951-1fa400-186bae83360c8; WEBDFPID=53u95wx422w0508xz522607844y4xw78813uw22z0yu979585yu41649-1994649710534-1679289709588WKIQOIQfd79fef3d01d5e9aadc18ccd4d0c95072951; token=AgGuIH7F2qba6g4ZAHGUSX4d_V5OW9sA2nmg-UfBPDD5597Lj6HWXTIOaSUIl96m-Qvg5XuAujozDAAAAABPFwAAEp9O8WY8h9inz3QsRE834azT4IgUeLmlvcU2brIvSexkceuJjJoTHBFVrARZGsSC; uid=1097461883; uid.sig=Qzn0f6oHqGvrFPGYvWuz1uoqSK0; _csrf=01ce4fdd7998e7af0a970f77df889e7dd5e9a8740e9301df0173d31238cb7646; Hm_lvt_703e94591e87be68cc8da0da7cbd0be2=1679014014,1679272915,1679278384,1679358096; _lx_utm=utm_source%3DBaidu%26utm_medium%3Dorganic; _lxsdk=24A0ABE0BCB711EDBCBCAB7DE9BBBE745660E51F7B56473198C812EC153C462A; __mta=188478359.1678930917547.1679378973144.1679379486522.61; Hm_lpvt_703e94591e87be68cc8da0da7cbd0be2=1679379526; _lxsdk_s=18702c97996-54b-157-ec6%7C%7C8'
    }
    if len(movies_to_fetch) == 0:
        print('all fetch complete')
    for movie in movies_to_fetch:
        url = base_url % movie[0]
        try:
            response = net_helper.get(url, header=header)
        except Exception as e:
            print('Failed: Connection Error %d' % int(movie[0]))
            continue
        if '猫眼验证' in response.text:
            print('请手动验证 %d' % int(movie[0]))
            time.sleep(random.randint(5, 15))
            continue

        root = BeautifulSoup(response.text, 'html.parser')
        want_items = root.find_all('div', class_='add-want-item-th')
        target = None
        for want_item in want_items:
            title = want_item.find('div', class_='title')
            if title.text == '累计想看':
                target = want_item
                break
        if target is None or target.find('span', class_='number').text == '--':
            sql = 'UPDATE movies_to_fetch_from_maoyan SET wanted_fetched=2, fetch_time="%d" WHERE mmid=%d' % \
                  (int(time.time()), int(movie[0]))
            connector.execute(sql)
            print('SUCCESS No Data %d' % int(movie[0]))
            time.sleep(random.randint(5, 15))
            continue
        wanted_count = target.find('span', class_='number').text

        sql = 'UPDATE movies_ratings SET wanted="%d" WHERE mmid="%d"' % (int(wanted_count), int(movie[0]))
        if connector.execute(sql):
            sql = 'UPDATE movies_to_fetch_from_maoyan SET wanted_fetched=1, fetch_time="%d" WHERE mmid=%d' % \
                  (int(time.time()), int(movie[0]))
            connector.execute(sql)
            print('SUCCESS wanted %d' % int(movie[0]))
        else:
            print('FAILED wanted %d' % int(movie[0]))
        time.sleep(random.randint(5, 15))
    connector.close()
