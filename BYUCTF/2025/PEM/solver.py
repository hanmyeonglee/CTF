from Crypto.PublicKey import RSA
from Crypto.Util.number import long_to_bytes
from math import isqrt

# PEM 파일에서 공개키 읽기
with open('ssh_host_rsa_key.pub', 'rb') as f:
    pem_data = f.read()

# 공개키 디코드
public_key = RSA.import_key(pem_data)

n, e = public_key.n, public_key.e
flag = long_to_bytes(isqrt(n)).decode()
print(flag)
