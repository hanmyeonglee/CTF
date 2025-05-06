from pwn import remote

path, port = "sspj.challs.srdnlen.it", 1717
program = remote(path, port)

program.sendline(b'\(')
program.interactive()