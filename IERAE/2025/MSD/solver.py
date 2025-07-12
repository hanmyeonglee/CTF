from pwn import remote, process
from random import randint

path, port = '34.146.49.83', 12345
program = remote(path, port)

for _ in range(100):
    numlist = []
    for _ in range(2000):
        mod = randint(10 ** 30, 10 ** 60)
        numlist.append(str(mod) + '\n')
    
    payload = ''.join(numlist) + '1\n'

    stage = program.recvline(keepends=False).decode()
    print(stage)
    program.send(payload.encode())
    program.recvuntil(b'most? : ')
    result = program.recvline(keepends=False).decode()
    print(result)

program.interactive()