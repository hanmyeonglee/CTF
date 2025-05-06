from pwn import remote


def xor(bytes1: bytes, bytes2: bytes) -> bytes:
    return bytes([b1 ^ b2 for b1, b2 in zip(bytes1, bytes2)])


def refresh(program: remote):
    program.recvuntil(b'~ Here is your encryption:\n|\n|   ')


def enc(program: remote, x: bytes) -> bytes:
    payload = b'0' * 64 + x.hex().encode()
    program.sendline(payload)
    refresh(program)

    txt = program.recvline(keepends=False).decode()
    return bytes.fromhex(txt)[48:64]


def dec(program: remote, x: bytes, enc0: bytes) -> bytes:
    payload = xor(enc0, x)
    payload = payload.hex().encode() + b'0' * 64
    program.sendline(payload)
    refresh(program)

    txt = program.recvline(keepends=False).decode()
    result = bytes.fromhex(txt)[48:64]
    return xor(result, enc0)


path, port = "confusion.challs.srdnlen.it", 1338
program = remote(path, port)


program.recvuntil(b"Let's try to make it confusing\n|\n|    flag = ")
eflag = bytes.fromhex(program.recvline(keepends=False).decode())
iv, eflag = eflag[:16], [eflag[i : i+16] for i in range(16, len(eflag), 16)]


enc0 = enc(program, bytes(16))
flag = [iv, dec(program, eflag[0], enc0)]
for i in range(1, len(eflag)):
    res = xor(eflag[i], flag[-1])

    s0 = enc(program, flag[-1])
    x = xor(s0, flag[-2])
    param = dec(program, x, enc0)

    res = xor(res, param)
    flag.append(dec(program, res, enc0))

flag.pop(0)
print(b''.join(flag))