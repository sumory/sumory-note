import json
import gevent
import gevent.core
import gevent.server
from lib import util
from lib import merkletree
from lib import coinbaser
from lib import coinbasetx
from lib import halfnode
from lib import block_template
from lib import bitcoin_rpc
from lib import template_registry
from lib import block_updater
from lib import logger
from lib import exceptions
import settings
import time
import StringIO
import binascii
import struct
import random
import geventhttpclient
from database import *

try:
    db=get_pooled_mysql_db()
    print 'finished db initialization, got db connection'
except Exception, e:
    print 'failed db initialization: %s' % e
    exit()


all_clients = set()


'''
        job_id = self.job_id
        prevhash = binascii.hexlify(self.prevhash_bin)
        (coinb1, coinb2) = [ binascii.hexlify(x) for x in self.vtx[0]._serialized ]
        merkle_branch = [ binascii.hexlify(x) for x in self.merkletree._steps ]
        version = binascii.hexlify(struct.pack(">i", self.nVersion))
        nbits = binascii.hexlify(struct.pack(">I", self.nBits))
        ntime = binascii.hexlify(struct.pack(">I", self.curtime))
        clean_jobs = True
'''

rpc = bitcoin_rpc.BitcoinRPC(settings.BITCOIN_RPC_HOST, settings.BITCOIN_RPC_PORT, settings.BITCOIN_RPC_USER, settings.BITCOIN_RPC_PASS)

def broadcast(broadcast_args):
    print '%s broadcasting' % time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())) 
    for client in all_clients:
        try:
            client.call('mining.notify', *broadcast_args)
        except:
            pass

def on_template_callback(*args, **kwargs):
    broadcast_args = registry.get_last_broadcast_args()
    broadcast(broadcast_args)

def on_block_callback(*args, **kwargs):
    job_id, prevhash, coinb1, coinb2, merkle_branch, version, nbits, ntime, clean_jobs = registry.get_last_broadcast_args()
    broadcast((job_id, prevhash, coinb1, coinb2, merkle_branch, version, nbits, ntime, True))

registry = template_registry.TemplateRegistry(block_template.BlockTemplate,
                            rpc,
                            settings.INSTANCE_ID,
                            on_template_callback, on_block_callback)

block_updater.BlockUpdater(registry, rpc)

class Client(object):
    def __init__(self, sock, address):
        self.sock = sock
        self.address = address
        self.fileobj = sock.makefile()
        self.username = None
        self.extranonce2_size = 4
        self.jobs = {}

    def get_request(self):
        line = self.fileobj.readline()
        if not line:
            return
        #logger.log('client', 'recv %s:%s %s' % (self.address[0], self.address[1], line.strip()))
        request = json.loads(line)
        return request

    def call(self, method, *args):
        obj = {
            'id': 1,
            'method': method,
            'params': args,
        }
        s = json.dumps(obj) + '\n'
        #logger.log('client', 'call %s:%s %s' % (self.address[0], self.address[1], s.strip()))
        self.fileobj.write(s)
        self.fileobj.flush()

    def response(self, request_id, result):
        obj = {
            'id': request_id,
            'result': result,
            'error': None,
        }
        s = json.dumps(obj) + '\n'
        #logger.log('client', 'resp %s:%s %s' % (self.address[0], self.address[1], s.strip()))
        self.fileobj.write(s)
        self.fileobj.flush()


# this handler will be run for each incoming connection in a dedicated greenlet
def connection_handler(sock, address):
    logger.log('debug', 'New connection from %s:%s' % address)

    client = Client(sock, address)

    try:
        all_clients.add(client)
        while True:
            request = client.get_request()
            if not request:
                logger.log('debug', 'client %s:%s disconnected.' % address)
                break

            if request['method'] == 'mining.subscribe':
                client.extranonce1 = struct.pack('<I', random.randrange(1 << 32))
                client.difficulty = settings.DIFFICULTY
                client.response(request['id'], [["mining.notify","asicme"], client.extranonce1.encode('hex'), 4])
                client.call('mining.set_difficulty', client.difficulty)
                job_id, prevhash, coinb1, coinb2, merkle_branch, version, nbits, ntime, clean_jobs = registry.get_last_broadcast_args()
                client.call('mining.notify', job_id, prevhash, coinb1, coinb2, merkle_branch, version, nbits, ntime, True)

            elif request['method'] == 'mining.authorize':
                worker_name = request['params'][0]

                print('auth worker: %s' % worker_name)
                try:
                    sql='SELECT * FROM pool_worker WHERE worker_name="%s"' % addslashes(worker_name)
                    logger.log('authorize', 'sql: %s' % (sql))
                    worker=db.one_dict(sql)
                    logger.log('authorize', 'query result: %s' % worker)
                except Exception, e:
                    logger.log('authorize', 'query exception: %s ' % e)
                    break

                if(worker==None):
                    logger.log('authorize', 'no worker: %s %s' % (address, worker_name))
                    break
                else:
                    client.username = worker_name
                    if('difficulty' in worker):
                        diff = worker['difficulty']
                        logger.log('authorize', 'set custome-diff: %s' % diff)
                    else:
                        diff = settings.DIFFICULTY
                        logger.log('authorize', 'set default-diff: %s' % diff)
                    client.difficulty = diff
                    client.call('mining.set_difficulty', client.difficulty)
                    client.response(request['id'], True)

            elif request['method'] == 'mining.submit':
                # oh yeah
                # {"params": ["slush.miner1", "bf", "00000001", "504e86ed", "b2957c02"], "id": 4, "method": "mining.submit"}
                
                worker_name, job_id, extranonce2, ntime, nonce = request['params']
                
                # for calculate hashrate of the workers
                logger.log('hashrate', '%s %s' % (worker_name, client.difficulty))                

                extranonce1_bin = client.extranonce1
                if not extranonce1_bin:
                    break

                submit_time = time.time()

                result = False
                try:
                    submit_result = registry.submit_share(job_id, worker_name, extranonce1_bin, extranonce2, ntime, nonce, client.difficulty)
                    result = True
                except exceptions.SubmitException, e:
                    logger.log('submit_exception','worker %s except %s' % (worker_name, e))
                    result = True
                    # break
                    pass
                except:
                    pass

                client.response(request['id'], result)


    except BaseException, e:
        logger.log('fail_client','worker %s:%s except %s' % (client.address[0],client.address[1],e))
        raise
    finally:
        all_clients.remove(client)
        logger.log('fail_client','worker %s:%s removed' % (client.address[0],client.address[1]))


if __name__ == '__main__':
    server = gevent.server.StreamServer(('0.0.0.0', 80), connection_handler)
    server.serve_forever()
