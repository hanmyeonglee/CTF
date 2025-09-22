import requests

URL = 'http://localhost:3000'

res = requests.get(URL + '/./', timeout=5)
print(res.text)