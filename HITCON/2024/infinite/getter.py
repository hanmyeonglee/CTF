import socks
import socket
import requests
import json
token = '2544876c41de80488474ee6f64b3f25d'
url = 'http://10.102.100.20:8000'

def proxy():
    socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 9000)
    socket.socket = socks.socksocket
    print('Proxy Conencted')


proxy()

res = requests.post(
    url + '/bounty/get',
    params={
        'target_team_id': 1
    },
    data={
        'target_team_id': 1
    }
).json()

print(json.dumps(res, indent=1))

