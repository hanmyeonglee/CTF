from pwn import *

context.arch = 'amd64'

with open("d8", "rb") as f:
    d8 = bytearray(f.read())
with open("node", "rb") as f:
    node = bytearray(f.read())

d8_part = d8[0x917E8E : 0x917E8E + 23]
node_part = node[0x127497A : 0x127497A + 23]

print(d8_part.hex())
print(disasm(d8_part))
print()
print(node_part.hex())
print(disasm(node_part))
print()

MASK = 0xFFFFFFFFFFFFFFFF
p64 = lambda x: struct.pack("<Q", x)

s0 = -1 & MASK
s1 = -1 & MASK
ps0 = b"\x49\xbe" + p64(s0) + b"\x48\xb9" + p64(s1) + b"\x48\x89\xc8"
ps1 = b"\x49\xbe" + p64(s0) + b"\x48\xb9" + p64(s1) + b"\x90" * 3

print(ps0.hex())
print(disasm(ps0))
print()
print(ps1.hex())
print(disasm(ps1))