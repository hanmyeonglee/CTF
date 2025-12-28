from pwn import remote

AND = lambda x, y: [a & b for a, b in zip(x, y)]
IOR = lambda x, y: [a | b for a, b in zip(x, y)]

HOST, PORT = 'crypto.heroctf.fr', 9000
p = remote(HOST, PORT)

def get_a_and_o():
    p.recvuntil(b'a = ')
    a = bytes.fromhex(p.recvline().strip().decode())
    p.recvuntil(b'o = ')
    o = bytes.fromhex(p.recvline().strip().decode())
    return a, o

a, o = get_a_and_o()
fl = bytes(len(a))
ag = bytes([0xFF] * len(o))

p.send(b'\n' * 100)

for _ in range(100):
    a, o = get_a_and_o()

    fl = bytes(IOR(fl, a))
    ag = bytes(AND(ag, o))

flag = fl + ag
print(flag.decode())