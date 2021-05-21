import requests
import time
import sys
MIN_AMOUNT = 10000000000000000
DEBUG_API = ''

def getDebugApi(port):
    return 'http://localhost:{}'.format(port)

def getPeers():
    global DEBUG_API
    response = requests.get('{}/chequebook/cheque'.format(DEBUG_API))

    data = response.json()
    if type(data) is dict and data.has_key('lastcheques'):
        return list(map(lambda x: x['peer'], data['lastcheques']))
    return []

def cashout(peer):
    global DEBUG_API
    response = requests.post('{}/chequebook/cashout/{}'.format(DEBUG_API, peer))

    if type(response.json()) is not dict or not response.json().has_key('transactionHash'):
        print "could not cashout cheque for {}: {}".format(peer, response)
        return
    txHash = response.json()['transactionHash']

    print "cashing out cheque for {} in transactionHash {}".format(peer, txHash)

    result = requests.get('{}/chequebook/cashout/{}'.format(DEBUG_API, peer))
    while type(result.json()) is not dict or not result.json().has_key('result'):
        time.sleep(5)
        result = requests.get('{}/chequebook/cashout/{}'.format(DEBUG_API, peer))

def getUncashedAmount(peer):
    global DEBUG_API
    response = requests.get('{}/chequebook/cashout/{}'.format(DEBUG_API, peer))
    if response.json().has_key('uncashedAmount') and response.json().get('uncashedAmount') is not None:
        return response.json()['uncashedAmount']
    return 0

def cashoutAll(min_amount = MIN_AMOUNT):
    peers = getPeers()
    for peer in peers:
        uncashedAmount = getUncashedAmount(peer)
        if uncashedAmount > min_amount:
            print "uncashed cheque for {} {} uncashed".format(peer, uncashedAmount)
            cashout(peer)

def listAllUncashed():
    peers = getPeers()
    for peer in peers:
        uncashedAmount = getUncashedAmount(peer)
        if uncashedAmount > 0:
            print "uncashed peer {} {} uncashed".format(peer, uncashedAmount)

if __name__ == '__main__':
    for i in range(3):
        port = 1635 + i * 100
        DEBUG_API = getDebugApi(port)

        if len(sys.argv) < 2 or sys.argv[1] == 'listAllUncashed':
            listAllUncashed()
        elif sys.argv[1] == 'cashout':
            cashout(sys.argv[2])
        elif sys.argv[1] == 'cashoutAll':
            cashoutAll(int(sys.argv[2]))

# python cashout.py cashoutAll 0
