from time import time
import requests

path = 'http://host3.dreamhack.games:18331/bot'

a = time()
requests.post(path, data={'name': 'fuck'})
print(time() - a)