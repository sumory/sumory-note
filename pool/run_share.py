#!/usr/bin/env python

import sys
import time
import umysql

db = umysql.Connection()
db.connect('localhost', 3306, 'root', 'asicmeroot', 'asicme_test')

share_log = open('logs/share.log')

processed = open('share.log.pos', 'r+')
pos = processed.read()
if pos:
    share_log.seek(int(pos))

def process_log(start=0):
    to_add = {}

    def commit():
        for (username, worker_name), item in to_add.iteritems():
            try:
                db.query('INSERT INTO pool_worker (user_id, woker_name) VALUES (%s, %s)', (123, 'w1'))
            except umysql.SQLError:
                pass
            sql = 'UPDATE pool_worker SET accepted_shares = accepted_shares + %s, last_share_time = %s WHERE user_id = %s AND woker_name = %s LIMIT 1'
            params = (item['shares'], item['last_share'], 123, worker_name)
            print sql, params
        to_add.clear()

        processed.seek(0)
        processed.write(str(share_log.tell()))
        processed.flush()

    while True:

        if len(to_add) >= 1000:
            commit()

        line = share_log.readline()
        if not line:
            commit()
            time.sleep(2)
            continue

        print share_log.tell()
        line_splitted = line.strip().split()
        if len(line_splitted) != 7:
            continue

        datetimestr = line_splitted[0] + ' ' + line_splitted[1]
        worker = line_splitted[2]

        worker_splitted = worker.split('.')

        if len(worker_splitted) != 2:
            continue

        username, worker_name = worker_splitted

        to_add.setdefault((username, worker_name), {
            'shares': 0,
            'last_share': None,
        })

        to_add[username, worker_name]['shares'] += 1
        to_add[username, worker_name]['last_share'] = datetimestr


if __name__ == '__main__':
    process_log()
