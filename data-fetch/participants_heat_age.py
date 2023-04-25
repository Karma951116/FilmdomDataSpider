from NetworkHelper import NetworkHelper
from MysqlConnector import MysqlConnector
from ConfigHelper import Config

import json
import time
import random

age_base_url = 'http://index.baidu.com/api/SocialApi/baseAttributes?wordlist[]='

if __name__ == '__main__':
    net_helper = NetworkHelper()
    connector = MysqlConnector()
    config = Config()
    config.read_config_src('general.ini')
    target_year = config.config_parser.get('General', 'target_year')
    connector.connect()
    sql = 'SELECT mpid, name_zh FROM participants_to_fetch_from_maoyan WHERE heat_age_fetched=0 or heat_gender_fetched=0'
    participant_to_fetch = connector.search(sql)
    header = {
        'Connection': 'keep-alive',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36',
        'Cookie': 'BIDUPSID=2F7F5B5793003D99DC69AEB992C0CE6F; PSTM=1680136735; BAIDUID=2F7F5B5793003D9962072F37EDBCA924:FG=1; MCITY=-131%3A; BDUSS=24zOE5EVE1TVWVZN0V2cmdiczQ0VXpNVHpkU3NPSEV-MnVrejFSazRlWXAtRlZrRVFBQUFBJCQAAAAAAAAAAAEAAABP2OwJY2d4dG90bwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAClrLmQpay5ka; BDORZ=B490B5EBF6F3CD402E515D22BCDA1598; BAIDUID_BFESS=2F7F5B5793003D9962072F37EDBCA924:FG=1; BA_HECTOR=248l8k2l2020802105a00k511i39cp81m; ZFY=XA5:Ac3Xtd2ntdW0rckeFrQETxDM8QUH1sZF7P3XsOqU:C; BDRCVFR[feWj1Vr5u3D]=I67x6TjHwwYf0; PSINO=1; delPer=0; Hm_lvt_d101ea4d2a5c67dab98251f0b5de24dc=1680746232,1680856736,1681042140,1681185544; bdindexid=kb8ot1jh6dst8tqm982giuj536; SIGNIN_UC=70a2711cf1d3d9b1a82d2f87d633bd8a04311980077g26FL9jq7AH%2Fr8OtzqxdA4Clhxg1HAcARj%2Bt0ESean5hJMQPpwm1%2FHoGPTuUdw0DNTUh3UutKjPzz7CPq7qPLGeFvaQOUMKWwS6vGqycpTo2z%2BR3CKotS00XH4T1gOz1E5%2BviO%2BNZTbcRYhLVFPnxSzaePPcYZks9qNLR%2BljRYsdM%2F9of%2F9jxIdjlDZEeqJYVd7p7J0uPoF3ijat1s42Bp9DafOdjJIH2E6OSNsGCrrU%2Blqa7FuLHQIGGiilJr5Bw25m7mu0eriYd6HQwwtXrQ%3D%3D33295720629514260136122790909865; __cas__rn__=431198007; __cas__st__212=e8e21320be47d8d489aa8e77b77b1543b8f8910a22499a1f2f58aed9b391dbf9db2c0438db261f17f21c6dd2; __cas__id__212=45881672; CPID_212=45881672; CPTK_212=1055465970; H_PS_PSSID=36551_38470_38440_38468_38290_38375_38485_37922_38343_26350_22157_38283; BCLID=8636954214713666187; BCLID_BFESS=8636954214713666187; BDSFRCVID=1iIOJexroG0wAwcfbyS5rFH_YcpWxY5TDYrEOwXPsp3LGJLVc4HAEG0Pts1-dEu-S2EwogKK0mOTHv-F_2uxOjjg8UtVJeC6EG0Ptf8g0M5; BDSFRCVID_BFESS=1iIOJexroG0wAwcfbyS5rFH_YcpWxY5TDYrEOwXPsp3LGJLVc4HAEG0Pts1-dEu-S2EwogKK0mOTHv-F_2uxOjjg8UtVJeC6EG0Ptf8g0M5; H_BDCLCKID_SF=tRAOoC8-fIvEDRbN2KTD-tFO5eT22-usWNQt2hcHMPoosIJ6LJJjb4DuyUoH0fvdyC7j--nwJxbUotoHXh3tMt_thtOp-CrpKbn75l5TtUJMqIDzbMohqqJXQqJyKMnitIj9-pnKHlQrh459XP68bTkA5bjZKxtq3mkjbPbDfn028DKuDj-WDjJXeaRabK6aKC5bL6rJabC3DnOoXU6q2bDeQN3f3Rb25DrIaM7-3qnroJOx3n7Zjq0vWq54WbbvLT7johRTWqR4HIbSLfonDh83KNLLKUQtHGAHK43O5hvvhb6O3M7-qfKmDloOW-TB5bbPLUQF5l8-sq0x0bOte-bQXH_EJ6tOtRAHVIvVaJbqJ5rP-trf5DCShUFs04CJB2Q-XPoO3KJbEt3nb45BhT_XQ47dX4JjQ5bk_xbgy4op8MJIMtQEhf0Z5ecp55370mTxoUJ2-KDVeh5Gqq-KQJ-ebPRiJPr9QgbqslQ7tt5W8ncFbT7l5hKpbt-q0x-jLTnhVn0MBCK0hD89Dj-Ke5PVKgTa54cbb4o2WbCQQU7m8pcN2b5oQT8WLqJ2Ktj8LKrHKqn7yRO2SPnXjqOUWJDkXpJvQnJjt2JxaqRCKKb1Eq5jDh3MKToDb-oteltH36vy0hvctn6cShnCqfjrDRLbXU6BK5vPbNcZ0l8K3l02V-bIe-t2XjQhDH-OJ6tHfn3aQ5rtKRTffjrnhPF3DtFPXP6-hnjy3bRf543J5JoBVI54Qx7rWttQ3p7ktl3Ry6r42-39LPO2hpRjyxv4-T0nLtoxJpOJ-bCL0p5aHx8Kst3vbURvD-ug3-7qex5dtjTO2bc_5KnlfMQ_bf--QfbQ0hOhqP-jBRIE3-oJqC8WhKDw3J; H_BDCLCKID_SF_BFESS=tRAOoC8-fIvEDRbN2KTD-tFO5eT22-usWNQt2hcHMPoosIJ6LJJjb4DuyUoH0fvdyC7j--nwJxbUotoHXh3tMt_thtOp-CrpKbn75l5TtUJMqIDzbMohqqJXQqJyKMnitIj9-pnKHlQrh459XP68bTkA5bjZKxtq3mkjbPbDfn028DKuDj-WDjJXeaRabK6aKC5bL6rJabC3DnOoXU6q2bDeQN3f3Rb25DrIaM7-3qnroJOx3n7Zjq0vWq54WbbvLT7johRTWqR4HIbSLfonDh83KNLLKUQtHGAHK43O5hvvhb6O3M7-qfKmDloOW-TB5bbPLUQF5l8-sq0x0bOte-bQXH_EJ6tOtRAHVIvVaJbqJ5rP-trf5DCShUFs04CJB2Q-XPoO3KJbEt3nb45BhT_XQ47dX4JjQ5bk_xbgy4op8MJIMtQEhf0Z5ecp55370mTxoUJ2-KDVeh5Gqq-KQJ-ebPRiJPr9QgbqslQ7tt5W8ncFbT7l5hKpbt-q0x-jLTnhVn0MBCK0hD89Dj-Ke5PVKgTa54cbb4o2WbCQQU7m8pcN2b5oQT8WLqJ2Ktj8LKrHKqn7yRO2SPnXjqOUWJDkXpJvQnJjt2JxaqRCKKb1Eq5jDh3MKToDb-oteltH36vy0hvctn6cShnCqfjrDRLbXU6BK5vPbNcZ0l8K3l02V-bIe-t2XjQhDH-OJ6tHfn3aQ5rtKRTffjrnhPF3DtFPXP6-hnjy3bRf543J5JoBVI54Qx7rWttQ3p7ktl3Ry6r42-39LPO2hpRjyxv4-T0nLtoxJpOJ-bCL0p5aHx8Kst3vbURvD-ug3-7qex5dtjTO2bc_5KnlfMQ_bf--QfbQ0hOhqP-jBRIE3-oJqC8WhKDw3J; RT="z=1&dm=baidu.com&si=6a608759-9838-48cb-aa13-1f346933141b&ss=lgbt4agz&sl=5&tt=3bj&bcn=https%3A%2F%2Ffclog.baidu.com%2Flog%2Fweirwood%3Ftype%3Dperf"; Hm_lpvt_d101ea4d2a5c67dab98251f0b5de24dc=1681190017; BDUSS_BFESS=24zOE5EVE1TVWVZN0V2cmdiczQ0VXpNVHpkU3NPSEV-MnVrejFSazRlWXAtRlZrRVFBQUFBJCQAAAAAAAAAAAEAAABP2OwJY2d4dG90bwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAClrLmQpay5ka; ab_sr=1.0.1_MGFkNGNjYTlmNTQwNDk0NjNiMjA0OWVkNTliYWUzNWY0NTlkYWI5YTFiMzM0ZmMzMDBkZTY1MDAxOWE1YjVjODI5NWQwNzk0NDQ2NWMyN2JiNGJiNjRkZGFkZWQwNzEzN2IwNzNkOWYzNmE0YzI5ZTc0NGIzMzM3OWEzYTlkZGQzMzc1YjU2MTAwNWU4ZGE3YTNkZjhjMDkxMTI5MDk0ZA=='
    }
    for participant in participant_to_fetch:
        name_zh = participant[1]
        url = age_base_url + name_zh
        try:
            response = net_helper.get(url, header=header)
        except Exception as e:
            print('Failed: Connection Error %d' % int(participant[0]))
            continue
        root = json.loads(response.text)
        try:
            age_rate = ''
            age_bundle = root['data']['result'][0]['age']
            for age in age_bundle:
                age_rate += str(age['rate'])
                age_rate += ','
            age_rate = age_rate.rstrip(',')
            if age_rate != '':
                sql = 'UPDATE participant_baidu_heat SET age_rate="%s" WHERE mpid="%d"' \
                      % (age_rate, int(participant[0]))
                if connector.execute(sql):
                    sql = 'UPDATE participants_to_fetch_from_maoyan SET heat_age_fetched=1, fetch_time="%d" WHERE mpid=%d' % \
                          (int(time.time()), int(participant[0]))
                    connector.execute(sql)
                    print('SUCCESS heat_age %d' % int(participant[0]))
                else:
                    print('FAILED heat_age %d' % int(participant[0]))
        except Exception as e:
            sql = 'UPDATE participants_to_fetch_from_maoyan SET heat_age_fetched=2, fetch_time="%d" WHERE mpid=%d' % \
                  (int(time.time()), int(participant[0]))
            connector.execute(sql)

        try:
            gender_rate = ''
            gender_bundle = root['data']['result'][0]['gender']
            for gender in gender_bundle:
                gender_rate += str(gender['rate'])
                gender_rate += ','
            gender_rate = gender_rate.rstrip(',')
            if age_rate != '':
                sql = 'UPDATE participant_baidu_heat SET gender_rate="%s" WHERE mpid="%d"' \
                      % (age_rate, int(participant[0]))
                if connector.execute(sql):
                    sql = 'UPDATE participants_to_fetch_from_maoyan SET heat_gender_fetched=1, fetch_time="%d" WHERE mpid=%d' % \
                          (int(time.time()), int(participant[0]))
                    connector.execute(sql)
                    print('SUCCESS heat_gender %d' % int(participant[0]))
                else:
                    print('FAILED heat_gender %d' % int(participant[0]))
        except Exception as e:
            sql = 'UPDATE participants_to_fetch_from_maoyan SET heat_gender_fetched=2, fetch_time="%d" WHERE mpid=%d' % \
                  (int(time.time()), int(participant[0]))
            connector.execute(sql)
        time.sleep(random.randint(5, 15))
    connector.close()
