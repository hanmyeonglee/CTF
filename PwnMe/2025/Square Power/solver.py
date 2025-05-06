from Crypto.Cipher import AES
from hashlib import sha256
from output import n, g, k, A, B, enc

enc = bytes.fromhex(enc)

key = (A - 1) * (B - 1) * pow(k, -1, n ** 2) // n + 1
key %= n ** 2

hash_secret_key = sha256(str(key).encode()).digest()
flag = AES.new(hash_secret_key, AES.MODE_ECB).decrypt(enc).decode()

print(f'{flag = }')