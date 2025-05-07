import hashlib, json, base64

from Crypto.Util.number import getPrime

def i2osp(x: int, x_len: int) -> bytes:
    return x.to_bytes(x_len, byteorder='big')

def os2ip(x_bytes: bytes) -> int:
    return int.from_bytes(x_bytes, byteorder='big')

def pkcs1_v1_5_encode(hash_bytes: bytes, em_len: int) -> bytes:
    # SHA-256 DER prefix
    der_prefix = bytes.fromhex("3031300d060960864801650304020105000420")
    t = der_prefix + hash_bytes
    ps_len = em_len - len(t) - 3
    if ps_len < 8:
        raise ValueError("Encoding error: PS too short")
    return b'\x00\x01' + b'\xff' * ps_len + b'\x00' + t

def rsa_sign(message: bytes, d: int, n: int) -> bytes:
    hash_bytes = hashlib.sha256(message).digest()
    k = (n.bit_length() + 7) // 8
    em = pkcs1_v1_5_encode(hash_bytes, k)
    m = os2ip(em)
    s = pow(m, d, n)
    return i2osp(s, k)

def rsa_verify(message: bytes, signature: bytes, e: int, n: int) -> bool:
    k = (n.bit_length() + 7) // 8
    s = os2ip(signature)
    m = pow(s, e, n)
    em = i2osp(m, k)

    hash_bytes = hashlib.sha256(message).digest()
    try:
        expected_em = pkcs1_v1_5_encode(hash_bytes, k)
    except ValueError:
        return False

    return em == expected_em

def jwt(header, payload, n, d):
    header = json.dumps(header)
    payload = json.dumps(payload)
    msg = f'{header}.{payload}'.encode()
    sign = rsa_sign(msg, d, n)

    return base64.urlsafe_b64encode(msg + b'.' + sign)


p = getPrime(1024)
q = getPrime(1024)
n = p * q
e = 0x10001
d = pow(e, -1, (p - 1) * (q - 1))

print(f'{p = }')
print(f'{q = }')
print(f'{n = }')
print(f'{e = }')
print(f'{d = }')