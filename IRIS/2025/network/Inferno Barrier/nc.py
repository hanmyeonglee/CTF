from pwn import remote
import base64
from time import sleep


def prom(program: remote, on: bool = True):
    program.sendline(f'prom {"on" if on else "off"}'.encode())

def initalize(program: remote):
    program.recvuntil(b'> ')

path = 'inferno-barrier.chal.irisc.tf'
port = 10500

program = remote(path, port)
sleep(5)
for _ in range(3): initalize(program)
prom(program)
while input('continue? : ') != 'n':
    l1 = program.recvline(keepends=False)
    l2 = program.recvline(keepends=False)
    print(l1)
    print(l2)
    print(base64.b64decode(l2).hex())
    initalize(program)