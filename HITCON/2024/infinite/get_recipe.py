import socks
import socket
import requests
import json

token = '2544876c41de80488474ee6f64b3f25d'
url = 'http://10.102.100.20:8000'

socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 9000)
socket.socket = socks.socksocket

while True:
    element = input('type element: ')
    res = requests.get(
        url + '/get_recipe',
        params={
            'team_token': token,
            'element': element
        }
    )

    print(json.dumps(res.json(), indent=1))
