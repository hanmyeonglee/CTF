from Crypto.Util.number import getPrime, long_to_bytes
from Crypto.Util.Padding import pad, unpad
from Crypto.Cipher import AES
from hashlib import sha256

import os

# generating strong parameters

flag = b"REDACTED" 

p = getPrime(1536)
g = p-1

a = getPrime(1536)
b = getPrime(1536)

A = pow(g, a, p)
B = pow(g, b, p)

assert pow(A, b, p) == pow(B, a, p)

key = pow(B, a, p)

print(g == key)

# Encrypting my message

key = long_to_bytes(key)
key = sha256(key).digest()[:16]

cipher = AES.new(key, AES.MODE_ECB)
ciphertext = cipher.encrypt(pad(flag, AES.block_size))

print(f"{p = }")
print(f"{g = }")
print("ciphertext =", ciphertext.hex())
