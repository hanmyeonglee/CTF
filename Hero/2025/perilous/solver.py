from cryptography.hazmat.decrepit.ciphers import algorithms
from cryptography.hazmat.primitives.ciphers import Cipher
from pwn import remote

HOST, PORT = 'crypto.heroctf.fr', 9001
p = remote(HOST, PORT)

key = b'NemoNemo'

p.sendline(key.hex().encode())
p.recvline()
p.recvuntil(b'flag k: ')
flag = bytes.fromhex(p.recvline(drop=True).decode())

p.close()

algorithm = algorithms.ARC4(key)
cipher = Cipher(algorithm, mode=None)
decryptor = cipher.decryptor()

flag = decryptor.update(flag)
print(flag.decode())