from distfiles.output import q, A, b, flag_ciphertext
from sage.all import *

AA = []
B = []
for i, e in enumerate(b):
    if not (145 <= (e % 256) < 256): continue
    B.append(e - (e % 256))
    AA.append(A[i])

R = Integers(q)
AA = matrix(R, AA)
B = vector(R, B)

s = AA.solve_right(B)

e = vector(b) - matrix(R, A) * s
sT = s.column()

flag = []
for i in range(0, len(flag_ciphertext), 8):
    bits = []
    for j in range(i, i + 8):
        a_sum, c = flag_ciphertext[j]
        r = s * vector(R, a_sum)
        d = (c - r) % q
        bits.append(int(d >= q // 2))
    flag.append(int(''.join(map(str, bits[::-1])), 2))

flag = bytes(flag).decode()
print(flag)