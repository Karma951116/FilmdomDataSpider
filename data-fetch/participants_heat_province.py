from NetworkHelper import NetworkHelper
from MysqlConnector import MysqlConnector
from ConfigHelper import Config

import json
import time
import random

province_base_url = 'https://index.baidu.com/api/SearchApi/region?region=0&word=%s&startDate=%d-01-01&endDate=%d-12-31&days='
province_code = {
    901: "山东", 902: "贵州", 903: "江西", 904: "重庆", 905: "内蒙古", 906: "湖北", 907: "辽宁",
    908: "湖南", 909: "福建", 910: "上海", 911: "北京", 912: "广西", 913: "广东", 914: "四川",
    915: "云南", 916: "江苏", 917: "浙江", 918: "青海", 919: "宁夏", 920: "河北", 921: "黑龙江",
    922: "吉林", 923: "天津", 924: "陕西", 925: "甘肃", 926: "新疆", 927: "河南", 928: "安徽",
    929: "山西", 930: "海南", 931: "台湾", 932: "西藏", 933: "香港", 934: "澳门"
}

if __name__ == '__main__':
    net_helper = NetworkHelper()
    connector = MysqlConnector()
    config = Config()
    config.read_config_src('general.ini')
    target_year = config.config_parser.get('General', 'target_year')
    connector.connect()
    sql = 'SELECT mpid, name_zh FROM participants_to_fetch_from_maoyan WHERE heat_province_fetched=0'
    participant_to_fetch = connector.search(sql)
    header = {
        'Connection': 'keep-alive',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36',
        'Cookie': 'BIDUPSID=2F7F5B5793003D99DC69AEB992C0CE6F; PSTM=1680136735; BAIDUID=2F7F5B5793003D9962072F37EDBCA924:FG=1; MCITY=-131%3A; BDUSS=24zOE5EVE1TVWVZN0V2cmdiczQ0VXpNVHpkU3NPSEV-MnVrejFSazRlWXAtRlZrRVFBQUFBJCQAAAAAAAAAAAEAAABP2OwJY2d4dG90bwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAClrLmQpay5ka; BDORZ=B490B5EBF6F3CD402E515D22BCDA1598; BA_HECTOR=8181aka4a1200h0l8k2h04191i34tvu1n; ZFY=XA5:Ac3Xtd2ntdW0rckeFrQETxDM8QUH1sZF7P3XsOqU:C; BAIDUID_BFESS=2F7F5B5793003D9962072F37EDBCA924:FG=1; delPer=0; PSINO=1; BDRCVFR[feWj1Vr5u3D]=I67x6TjHwwYf0; H_PS_PSSID=38185_36551_38470_38440_38306_38468_38290_38375_38486_37922_38343_26350_22157_38283_37881; BCLID=9973698255337250611; BCLID_BFESS=9973698255337250611; BDSFRCVID=x5AOJexroG0wAwcf-ihu2LjdgcpWxY5TDYrEOwXPsp3LGJLVc4HAEG0Pts1-dEu-S2EwogKK0mOTHv-F_2uxOjjg8UtVJeC6EG0Ptf8g0M5; BDSFRCVID_BFESS=x5AOJexroG0wAwcf-ihu2LjdgcpWxY5TDYrEOwXPsp3LGJLVc4HAEG0Pts1-dEu-S2EwogKK0mOTHv-F_2uxOjjg8UtVJeC6EG0Ptf8g0M5; H_BDCLCKID_SF=tRAOoC8-fIvDqTrP-trf5DCShUFshTQCB2Q-XPoO3KJbEt3nbCcEMbQXXM6bK-JjQ5bk_xbgy4op8P3y0bb2DUA1y4vp55370mTxoUJ2-KDVeh5Gqq-KQJ-ebPRiJPr9QgbqslQ7tt5W8ncFbT7l5hKpbt-q0x-jLTnhVn0MBCK0HPonHj8Be5503H; H_BDCLCKID_SF_BFESS=tRAOoC8-fIvDqTrP-trf5DCShUFshTQCB2Q-XPoO3KJbEt3nbCcEMbQXXM6bK-JjQ5bk_xbgy4op8P3y0bb2DUA1y4vp55370mTxoUJ2-KDVeh5Gqq-KQJ-ebPRiJPr9QgbqslQ7tt5W8ncFbT7l5hKpbt-q0x-jLTnhVn0MBCK0HPonHj8Be5503H; Hm_lvt_d101ea4d2a5c67dab98251f0b5de24dc=1680404536,1680746232,1680856736,1681042140; bdindexid=6jkhqpnl5aeuhbdo34feqgsop6; SIGNIN_UC=70a2711cf1d3d9b1a82d2f87d633bd8a04310546011WXgGi1zHoudR2jMgPh1g2TVVo0pXb%2BgGP4RrTBiJAr2pdmjDcPeA6iVpFpSU9NpigQIgasK%2FADtCytR0tD7g44Wt085kRb5seXKxK0AyJ0ZNCLHljN6FjWzg%2B9iX6tGIqnJXabvzgDPdH6prLIppiodvfwsSV4dcyfeYnuoyEO%2FUqpieSB%2BEmLnVg6jXnZUniJYOVriEEvUzdwCTKIyPaSeM4vmjfamUGPw1cTfvlxd4VNBYiY%2BYK2y%2Fn324IlhigscIO9kpa6TGRCgCODz1Gg%3D%3D49274889610501214981878266938633; __cas__rn__=431054601; __cas__st__212=0f7db57d035616aa2617e7ae3b2f44e0526c24455b0ff2b24deeebbcab26c710eed7f40a8028583d6afe4ad5; __cas__id__212=45881672; CPID_212=45881672; CPTK_212=1244632340; Hm_lpvt_d101ea4d2a5c67dab98251f0b5de24dc=1681042482; BDUSS_BFESS=24zOE5EVE1TVWVZN0V2cmdiczQ0VXpNVHpkU3NPSEV-MnVrejFSazRlWXAtRlZrRVFBQUFBJCQAAAAAAAAAAAEAAABP2OwJY2d4dG90bwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAClrLmQpay5ka; ab_sr=1.0.1_MmRkOThkZTkzYmViMGRmNmM0Yzk5MjM5MDM2ZDNmNTlhODIxMjYzMDI5NTY3Y2E3NTczMmFhZmIwZjhjNTE0YmMxMjM1NTRmMzc4YmI5YjI1ZmJhMzAwYzYxMDhhY2NjOTNhMWUwOWNhMGY4Y2ZlZTg3ZmVjNmJiNTAxMzkyODEzOGE5NzRiZGE2NWYwYmE2MWJhNzU2YWE5NDU4NWVkZA==; RT="z=1&dm=baidu.com&si=0bcfec0e-155d-42ff-8bb7-b446db9863bd&ss=lg9d34pu&sl=b&tt=9y1&bcn=https%3A%2F%2Ffclog.baidu.com%2Flog%2Fweirwood%3Ftype%3Dperf&ld=7deq"'
    }
    for participant in participant_to_fetch:
        name_zh = participant[1]
        url = province_base_url % (name_zh, int(target_year), int(target_year))
        try:
            response = net_helper.get(url, header=header)
        except Exception as e:
            print('Failed: Connection Error %d' % int(participant[0]))
            continue
        root = json.loads(response.text)
        prov = None
        try:
            prov = root['data']['region'][0]['prov']
        except Exception as e:
            sql = 'UPDATE participants_to_fetch_from_maoyan SET heat_province_fetched=2, fetch_time="%d" WHERE mpid=%d' % \
                  (int(time.time()), int(participant[0]))
            connector.execute(sql)
            print('SUCCESS heat %d' % int(participant[0]))
            time.sleep(random.randint(5, 15))
            continue

        if prov == '':
            sql = 'UPDATE participants_to_fetch_from_maoyan SET heat_province_fetched=2, fetch_time="%d" WHERE mpid=%d' % \
                  (int(time.time()), int(participant[0]))
            connector.execute(sql)
            print('SUCCESS heat %d' % int(participant[0]))
            time.sleep(random.randint(5, 15))
            continue
        province_rate = ''
        for key in prov.keys():
            prov_name = province_code[int(key)]
            value = prov[key]
            province_rate += prov_name
            province_rate += ','
            province_rate += str(value)
            province_rate += ','
        province_rate.rstrip(',')

        sql = 'INSERT IGNORE INTO participant_baidu_heat SET mpid="%d", name_zh="%s", province_rate="%s"' % \
              (int(participant[0]), name_zh, province_rate)
        if connector.execute(sql):
            sql = 'UPDATE participants_to_fetch_from_maoyan SET heat_province_fetched=1, fetch_time="%d" WHERE mpid=%d' % \
                  (int(time.time()), int(participant[0]))
            connector.execute(sql)
            print('SUCCESS heat_province %d' % int(participant[0]))
        else:
            print('FAILED heat_province %d' % int(participant[0]))
    connector.close()