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
    print '%s paying..' % time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
    logger.log('debug', 'pay start')

    try:
        sql = 'select id, user_id, user_name, amount, send_amount, bitcoin_address, status, time from pool_withdraw where status = 0'
        all_withdraw = db.all_dict(sql)
        logger.log('debug', 'need pay for %d withdraw' % len(all_withdraw))

        if(len(all_withdraw) != 0):
            try:
                rpc.walletpassphrase('123456', 15)
            except Exception,e:
                logger.log('error','walletpassphrase error %s' % e)

            for w in all_withdraw:
                try:
                    logger.log('pay', '+++++++++++++++++++++++++++++++++start one++++++++++++++++++++++++++++++++++++++++++++++++')
                    
                    withdraw_id = w['id']
                    username = w['user_name']
                    send_amount =  float(w['send_amount'])
                    address = 'mkaUYgNmoRJD9Y23DyXDCaN2aWaAaqey6j' #w['bitcoin_address']
                    balance = float(rpc.getbalance(wallet_account))
                    address_valid = rpc.validateaddress(address)

                    logger.log('pay','start %d %s %.8f %s' % (withdraw_id, username, send_amount, address))
                    
                    if(address_valid != True):
                        logger.log('pay', 'invalid address %s' % address)
                    elif(balance > send_amount):
                        
                        now = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
                        txid = rpc.sendfrom(wallet_account, address, send_amount)
                        sql = 'update pool_withdraw set status = 1,confirm_time="%s" where id = %d' % (now, withdraw_id)
                        db.run(sql)
                        if txid is not None:                            
                            logger.log('pay','txid %s' % txid)
                            sql = 'update pool_withdraw set status=1, bitcoin_transaction="%s", payment_user="%s", confirm_time="%s" where id = %d' % (txid, 'auto_pay', now, withdraw_id)
                            db.run(sql)
                            logger.log('pay', 'pay success')
                        else:
                            logger.log('pay','txid is None')
                    else:
                        logger.log('pay','not enough money to pay %s %.8f' % (username, send_amount))
                    logger.log('pay', '+++++++++++++++++++++++++++++++++end one++++++++++++++++++++++++++++++++++++++++++++++++++')
                except Exception, e:
                    logger.log('pay', 'exception %s' % e)
                    logger.log('error', 'Exception %s' %e)
                    logger.log('pay', '+++++++++++++++++++++++++++++++++end one++++++++++++++++++++++++++++++++++++++++++++++++++')
                    

        
    except exceptions.AutoPayException, e:
        logger.log('error','AutoPayException %s' % e)
    except BaseException, e:
        logger.log('error','BaseException %s' % e)
    except:
        pass
    finally:
        logger.log('debug','pay stop')


if __name__ == '__main__':
    forever = False
    if(forever is True):
        while True:
            pay()
            time.sleep(20)
    else:
        pay()
