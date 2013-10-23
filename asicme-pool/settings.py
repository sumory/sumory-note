
BITCOIN_RPC_HOST = '127.0.0.1'
BITCOIN_RPC_PORT = 8332
#BITCOIN_RPC_PORT = 18332
BITCOIN_RPC_USER = 'bitcoinrpc'
BITCOIN_RPC_PASS = 'BQyoWPo4EzmfNK7z4NrNejZSLqEwwiRd47tD78jSj6Rj'

BITCOIN_ADDRESSES = {
     #'1AYTkpQDA2nu6vu6JjZvbDgMXa1SjehVYu': 100
     '17uvo21YYPdFP5qoryTUwXkSjsmeYtkF6E': 100,
     '1Q2EpkH7SzSGCzYz18j3ctBL898LDpYeUn':100,
     '1LjoPc3ws8ij5LufnxYr2BuDQH8nBRQJqS':100
}

#default difficulty, if no diff set for the worker
DIFFICULTY = 1

COINBASE_EXTRAS = '/stratum/'
INSTANCE_ID = 10
PREVHASH_REFRESH_INTERVAL = 5
MERKLE_REFRESH_INTERVAL = 5

#roll log file or not
LOG_ROLL = True

#auth user or not
AUTH_USER = True

#mysql settings
DB_HOST='localhost'
DB_USER='root'
DB_PWD='123456'
DB_DB='asicme_pool'
DB_PORT=3306
