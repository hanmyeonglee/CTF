from pwn import remote

path, port = 'political-bot.chal.irisc.tf', 1337
program = remote(path, port)

program.sendline(b'asd')
program.interactive()