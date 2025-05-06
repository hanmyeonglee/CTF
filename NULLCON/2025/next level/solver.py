from Crypto.Util.number import isPrime, long_to_bytes
from gmpy2 import iroot
from pwn import remote

def nextprime(n):
	p = n
	while True:
		if isPrime(p := p+1): return p

def prevprime(n):
    p = n
    while True:
        if isPrime(p := p - 1): return p

path, port = '52.59.124.14', 5028
program = remote(path, port)

N = int(program.recvline(keepends=False).decode())
c = int(program.recvline(keepends=False).decode())

r = int(iroot(N, 3)[0])
if r % 2 == 0:
    r += 1

print('done #1')
r = nextprime(r)
print('done #2')
q = prevprime(r)
p = N // r // q

d = pow(0x10001, -1, (p - 1) * (q - 1) * (r - 1))
flag = long_to_bytes(pow(c, d, N))
print(f'{p = }')
print(f'{q = }')
print(f'{r = }')
print(f'{c = }')
print(f'{N = }')
print(f'{flag = }')