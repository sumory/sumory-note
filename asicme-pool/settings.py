
BITCOIN_RPC_HOST = '127.0.0.1'
BITCOIN_RPC_PORT = 8332
#BITCOIN_RPC_PORT = 18332
BITCOIN_RPC_USER = 'bitcoinrpc'
BITCOIN_RPC_PASS = 'BQyoWPo4EzmfNK7z4NrNejZSLqEwwiRd47tD78jSj6Rj'

BITCOIN_ADDRESSES = {
     '1AYTkpQDA2nu6vu6JjZvbDgMXa1SjehVYu': 100
     #'1MmYQSEtF3nmhGZcFLDhrNr7fWn5fehD9Z': 100,
     #'mn6QvZuSLp8gqQrgXvweS4doiBv5EMM3jT': 100,
     #'mqFwFYJ6btZRTinw3fTt6no1wXpKT3fURw':100,
     #'mvVUsS9JQ72AsHNegUVgA1mQFqQPuLfGDR':100
}

#default difficulty, if no diff set for the worker
DIFFICULTY = 10

COINBASE_EXTRAS = '/stratum/'
INSTANCE_ID = 10
PREVHASH_REFRESH_INTERVAL = 5
MERKLE_REFRESH_INTERVAL = 50

#roll log file or not
LOG_ROLL = True

#auth user or not
AUTH_USER = True

#mysql settings
DB_HOST='localhost'
DB_USER='root'
DB_PWD='123456'
DB_DB='asicme_test'
DB_PORT=3306
