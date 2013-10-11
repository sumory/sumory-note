#coding=utf-8
import json
import gevent
import gevent.core
import gevent.server
from lib import bitcoin_rpc
from lib import logger
from lib import exceptions
import settings
import time
import random
from database import *


'''
对于一个新bitcoind

1. encryptwallet 加密钱包
2. 首先建立一个account和在这个account下的N个地址，如建立'asicme_pool'账户
    getnewaddress asicme_pool
3. 查看asicme_pool账户下的所有地址
    getaddressesbyaccount asicme_pool
    [
        "mxwUCwhcRr5Fh3ctQAt4XmMjwgcxw9eq6E",
        "mkziUZMiH3BgDgGBT5ZZGqrH91tnBdbTR8"
    ]
4. 往以上地址充钱
5. 从asicme_pool往外打钱
   - getbalance asicme_pool 查看钱是否大于0
   - 解密 walletpassphrase 密码 时间
   - 有足够钱时打出去，sendfrom asicme_pool mnB43cJB4jceYQMt8ZjWVDpy7yKJbUM69S 0.0123
   - 获取上面的txid
'''

try:
    db = get_pooled_mysql_db()
    print 'succeed db initialization'
except Exception, e:
    print 'failed db initialization: %s' % e
    exit()


rpc = bitcoin_rpc.BitcoinRPC(settings.BITCOIN_RPC_HOST, settings.BITCOIN_RPC_PORT, settings.BITCOIN_RPC_USER, settings.BITCOIN_RPC_PASS)
wallet_account = settings.WALLET_ACCOUNT

def pay():
    logger.log('debug', 'pay start')

    try:
        sql='select id, user_id, user_name, amount, send_amount, bitcoin_address, status, time from pool_withdraw where status = 0'
        all_withdraw = db.all_dict(sql)
        #print(sql)
        #print(all_withdraw)
        print('need pay for %d withdraw' % len(all_withdraw))
        if(len(all_withdraw)!=0):
            rpc.walletpassphrase('123456', 60)
            for w in all_withdraw:
                #print(w)
                print('+++++++++++++++++++++++++++++++++start one++++++++++++++++++++++++++++++++++++++++++++++++')
                send_amount =  float(w['send_amount'])
                address = 'n4T6tGhoiS2KmykjWpjeHZJNqi65cTudpb' #w['bitcoin_address']
                balance = float(rpc.getbalance(wallet_account))
                if(balance > send_amount):
                    logger.log('pay','start %d %s %.8f %s' % (w['id'], w['user_name'], send_amount, address))
                    txid = rpc.sendfrom(wallet_account, address, 100000 if send_amount<9 else send_amount)
                    if txid is not None:
                        logger.log('pay','txid %s' % txid)
                    else:
                        logger.log('pay','txid is None')
                else:
                    logger.log('pay','not enough money to pay %s %.8f' % (w['user_name'],send_amount))
                print('+++++++++++++++++++++++++++++++++end one++++++++++++++++++++++++++++++++++++++++++++++++++')

        
    except exceptions.AutoPayException, e:
        logger.log('error','AutoPayException %s' % e)
    except BaseException, e:
        logger.log('error','BaseException %s' % e)
    except:
        pass
    finally:
        logger.log('debug','pay stop')


if __name__ == '__main__':
    print('启动auto-pay')
    pay()
