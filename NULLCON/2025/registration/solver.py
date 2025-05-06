from Crypto.Util.number import bytes_to_long, isPrime
from hashlib import sha256
from pwn import remote

def nextprime(x):
    while True:
        if isPrime(x := x + 2): return x

path, port = '52.59.124.14', 5026
program = remote(path, port)

program.recvuntil(b'n = ')
n = int(program.recvline(keepends=False).decode())
program.recvuntil(b'a = ')
a = int(program.recvline(keepends=False).decode())
program.recvuntil(b'e = ')
e = int(program.recvline(keepends=False).decode())

program.recvuntil(b'2) sign')

p = int(n ** 0.5)
if p % 2 == 0: p += 1
while n % p != 0:
    p = nextprime(p)
q = n // p

d = pow(e, -1, (p - 1) * (q - 1))

program.sendline(b'2')
program.recvuntil(b'Challenge: ')
h = bytes.fromhex(program.recvline(keepends=False).decode())
h = bytes_to_long(sha256(h).digest())

s = pow(a, h * d, n)
program.sendline(str(s).encode())
flag = program.recvline(keepends=False).decode()

print(f'{flag = }')
program.close()