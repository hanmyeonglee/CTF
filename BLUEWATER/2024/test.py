from Crypto.Util.number import getPrime

def egcd(a, b, sm):
    if a == 0:

        return (b, 0, 1, sm)

    g, y, x, sm = egcd(b%a, a, sm + 1)

    return (g, x - (b//a) * y, y, sm)

def modinv(a, m):
    g, x, y, sm = egcd(a, m, 1)
    if g != 1:
        raise Exception('No modular inverse')

    return x % m, sm


e = 0x10001
total = 0
for _ in range(100):
    print(_)
    p, q = getPrime(1024), getPrime(1024)
    d, sm = modinv(e, p * q)
    total += sm

print(total / 100)
