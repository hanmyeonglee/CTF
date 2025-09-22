import requests

URL = 'http://127.0.0.1:8000'
r = requests.post(URL + '/upload', files={'file': ('xss.html ', open('xss.html', 'rb'))})
print(r.text)