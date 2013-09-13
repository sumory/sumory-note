'''
    Implements simple interface to bitcoind's RPC.
'''

import json
import base64
import geventhttpclient
import logger

class BitcoinRPC(object):
    
    def __init__(self, host, port, username, password):
        self.client = geventhttpclient.HTTPClient(host, port)
        self.credentials = base64.b64encode("%s:%s" % (username, password))
        self.headers = {
            'Content-Type': 'text/json',
            'Authorization': 'Basic %s' % self.credentials,
        }
        
    def _call_raw(self, data):
        logger.log('rpc', 'req:', data)
        res = self.client.post('/', body=data, headers=self.headers).read()
        logger.log('rpc', 'res:', res)
        return res
           
    def _call(self, method, params):
        return self._call_raw(json.dumps({
                'jsonrpc': '2.0',
                'method': method,
                'params': params,
                'id': '1',
            }))

    def submitblock(self, block_hex):
        resp = self._call('submitblock', [block_hex])
        if json.loads(resp)['result'] == None:
            return True
        else:
            return False

    def getblocktemplate(self):
        resp = self._call('getblocktemplate', [])
        return json.loads(resp)['result']

    def prevhash(self):
        resp = self._call('getwork', [])
        try:
            return json.loads(resp)['result']['data'][8:72]
        except Exception as e:
            logger.log('error', "Cannot decode prevhash %s" % str(e))
            raise
                                                  
    def validateaddress(self, address):
        resp = self._call('validateaddress', [address])
        return json.loads(resp)['result']
