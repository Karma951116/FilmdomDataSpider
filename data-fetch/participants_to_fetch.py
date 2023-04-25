# Insert participants table use movies_participants
from MysqlConnector import MysqlConnector
import time

if __name__ == '__main__':
    connector = MysqlConnector()
    connector.connect()
    sql = 'SELECT mpid, name ' \
          'FROM movies_participants ' \
          'GROUP BY mpid, name'
    pariticipants_to_fetch = connector.search(sql)
    for participant in pariticipants_to_fetch:
        mpid = int(participant[0])
        name_zh = participant[1]
        sql = 'INSERT IGNORE INTO participants_to_fetch_from_maoyan ' \
              'SET mpid="%d", name_zh="%s", base_fetched=0, poster_fetched=0, awards_fetched=0, ' \
              'related_fetched=0, fetch_time="%d"' \
              % (mpid, name_zh, int(time.time()))
        if connector.execute(sql):
            print("SUCCESS %s, %d" % (name_zh, mpid))
        else:
            print("FAILED %s, %d" % (mpid, mpid))
    connector.close()