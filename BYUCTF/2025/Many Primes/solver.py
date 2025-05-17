from output import n, e, flag as enc
from Crypto.Util.number import long_to_bytes
from collections import Counter

sieve = [True] * (1 << 16 + 1)
sieve[0] = sieve[1] = False
primes = []
for i in range(2, 1 << 16 + 1):
    if not sieve[i]: continue
    for j in range(2 * i, 1 << 16 + 1, i):
        sieve[j] = False
    primes.append(i)

factors = []
i = 0
N = n
while N > 1:
    p = primes[i]
    if N % p == 0:
        N //= p
        factors.append(p)
    else:
        i += 1

factor_counter = Counter(factors)
factor_set = set(factors)

phi = n
for factor in factor_set:
    phi *= factor - 1
    phi //= factor

d = pow(e, -1, phi)
dec = pow(enc, d, n)
flag = long_to_bytes(dec).decode()

print(flag)