#!/usr/bin/env python3
import secrets

AND = lambda x, y: [a & b for a, b in zip(x, y)]
IOR = lambda x, y: [a | b for a, b in zip(x, y)]

with open("flag.txt", "rb") as f:
    flag = [*f.read().strip()]
    l = len(flag) // 2

while True:
    k = secrets.token_bytes(len(flag))
    a = AND(flag[:l], k[:l])
    o = IOR(flag[l:], k[l:])

    print("a =", bytearray(a).hex())
    print("o =", bytearray(o).hex())
    input("> ")
