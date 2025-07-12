from pwn import process, remote

def xor(x, y):
    return bytes([a ^ b for a, b in zip(x, y)])

pt = b'Slide to the leftSlide to the right'
#program = process(['python3', 'real-smooth.py'])
program = remote('smooth.chal.cyberjousting.com', 1350)
ct = bytes.fromhex(''.join(program.recvline(keepends=False).decode() for _ in range(2)))
stream = xor(pt, ct)

goal = b'Criss cross, criss cross'
enc = xor(goal, stream).hex().encode()
program.sendline(enc)

program.interactive()