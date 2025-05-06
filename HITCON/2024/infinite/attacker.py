import socks
import socket
import requests
import json
from time import sleep
import os
from search import search

token = '2544876c41de80488474ee6f64b3f25d'
url = 'http://10.102.100.20:8000'
config = {
    'available': ['earth', 'mountain', 'water', 'wind', 'thunder', 'fire', 'lake', 'sky']
}

def proxy():
    socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 9000)
    socket.socket = socks.socksocket
    print('Proxy Connected')

proxy()

for teamid in range(9, 14):
    if teamid == 6:
        continue

    res = requests.post(
        url + '/bounty/get',
        params={
            'target_team_id': teamid
        }
    ).json()

    target_product = res['target_product']

    print(requests.get(
        url + '/get_recipe',
        params={
            'team_token': token,
            'element': target_product
        }
    ).json())

    sleep(5)