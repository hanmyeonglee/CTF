import requests

PATH = 'http://hacktheon2025-challs-alb-1354048441.ap-northeast-2.elb.amazonaws.com:58709'

user = requests.Session()
res = user.post(
    PATH + '/api/signin',
    json={
        'username': 'guest',
        'password': 'guest'
    }
)
print(res.text)

res = user.get(PATH + '/api/flag')
print(res.text)