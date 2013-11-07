import settings
from lib import bitcoin_rpc

rpc = bitcoin_rpc.BitcoinRPC(settings.BITCOIN_RPC_HOST, settings.BITCOIN_RPC_PORT, settings.BITCOIN_RPC_USER, settings.BITCOIN_RPC_PASS)

block = rpc.getblock('00000000000000077e6eb274513df39076fc13ea85b775b8ed501b785b45f85d')
print block['confirmations']
print block['tx'][0]


coinbase = block['tx'][0]
tx = rpc.gettxout(coinbase,0)
print tx['value']


