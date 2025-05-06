from Crypto.Util.number import getStrongPrime
from math import gcd
from random import randint
from typing import Tuple
from Crypto.Cipher import AES
from hashlib import sha256

flag = b"PWNME{xxxxxxxxxxxxxxxxxxxxxxxxx}"

def generate_primes() -> int:
    p = getStrongPrime(512)
    q = getStrongPrime(512)

    while gcd(p*q, (p-1)*(q-1)) != 1:
        p = getStrongPrime(512)
        q = getStrongPrime(512)

    return p*q

def generate_public_key() -> Tuple[int, int]:
    n = generate_primes()
    k = randint(2, n-1)
    while gcd(k, n) != 1:
        k = randint(2, n-1)
    g = 1 + k * n
    return n, g, k

n, g, k = generate_public_key()

a = randint(2, n-1)
b = randint(2, n-1)


A = pow(g, a, n*n)
B = pow(g, b, n*n)

secret_key = pow(B, a, n*n)

def encrypt(m: bytes, secret_key: int) -> str:
    hash_secret_key = sha256(str(secret_key).encode()).digest()
    cipher = AES.new(hash_secret_key, AES.MODE_ECB)
    return cipher.encrypt(m).hex()




print(f"{n = }")
print(f"{g = }")
print(f"{k = }")

print(f"{A = }")
print(f"{B = }")

print(f'enc = "{encrypt(flag, secret_key)}"')



