import os
import requests

def gen_user():
    return os.urandom(8).hex(), os.urandom(8).hex()

URL = 'http://127.0.0.1:8000'

s = requests.Session()
email, password = gen_user()
s.post(f'{URL}/api/auth/register', data={'email': email, 'password': password})
s.post(f'{URL}/api/auth/login', data={'email': email, 'password': password})