import hashlib
from Crypto.Util.number import long_to_bytes
from pwn import remote

def test(goal, INPUT):
    return hashlib.sha256(
        goal + INPUT
    ).hexdigest().startswith('0' * 5)


def work(goal):
    i = 0
    while True:
        if test(goal, long_to_bytes(i)):
            print('success')
            return long_to_bytes(i)
        
        if i % 0x1000000 == 0:
            print(i)
        
        i += 1


path, port = 'bluesocial.chal.perfect.blue', 6900
program = remote(path, port)

line = program.recvuntil(b'):')
opn = line.find(b"b'")
clos = line.find(b"'", opn + 2)
goal = line[opn + 2 : clos]

print(line)
print(goal)

answer = work(goal)

print(answer)

program.sendline(answer)
program.interactive()