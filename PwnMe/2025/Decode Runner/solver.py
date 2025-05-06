from pwn import remote
from time import sleep
from decoder import get_func

path, port = 'decoderunner-500b25f0a836c016.deploy.phreaks.fr', 443

program = remote(path, port, ssl=True)
program.recvuntil(b'Good luck!\n')
program.recvline()
program.recvline()
program.recvline()

for _ in range(100):
    try:
        line = program.recvline(keepends=False).decode()
        if line.startswith('hint: '):
            hint = line[6:]
            ct = program.recvline(keepends=False).decode()[8:]
        elif line.startswith('cipher: '):
            hint = ''
            ct = line[8:]
        else:
            raise Exception(f'format error -> {line}')
        decode_func = get_func(hint)
        pt = decode_func(ct)
        print([_], hint if hint != '' else '<NATO>', '-', ct, '->', pt.decode())
        program.sendline(pt.lower())
    except EOFError:
        program.interactive()
        break
else:
    program.interactive()