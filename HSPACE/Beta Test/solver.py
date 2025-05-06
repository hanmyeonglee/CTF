from base64 import b64encode, b64decode
from Crypto.Cipher import AES
from Crypto.Util.number import bytes_to_long, long_to_bytes

def split_size_16(text: bytes) -> list[bytes]:
    ret = []
    for i in range(0, len(text), 16):
        ret.append(text[i:i+16])
    return ret


def rc(text: bytes, num: int) -> bytes:
    ret = []
    for t in text:
        for tmp in range(0x10000):
            if (tmp + num) % 256 == t:
                ret.append(tmp)
                break
        else:
            raise Exception('시발 c')
    
    return ret


def rb(text: bytes, num: int) -> bytes:
    ret = []
    for t in text:
        for tmp in range(0x10000):
            res = (tmp | ((tmp << num) >> (8 - num))) & 255
            if t == res:
                ret.append(tmp)
                break
        else:
            raise Exception('시발 b')
    
    return ret


def rd(text: bytes) -> bytes:
    ret = []
    for t in text:
        if chr(t).isalpha():
            tmp = t + 13
            if tmp > 122:
                tmp += (65 if chr(t).isupper() else 97) - 123
        else:
            tmp = t
        ret.append(tmp)

    return ret


def ra(text: bytes, salt: bytes) -> bytes:
    ret = []
    for i, t in enumerate(text):
        ret.append(t ^ salt[i])

    return ret


goal = b'vXR1VGYbvAEChVv+wQazyhyN9AXlTp2Kqoaz5Sm3FtxuJHJ+3BVRaeJ2PO+GmzZF'
password = b'd7mXTONUOhWIVHgy'
salt = b'buNj#7]0~!<ua:>\\\\'

enc_blocks = split_size_16(b64decode(goal))

block = enc_blocks[0]
enc_step1 = AES.new(password, AES.MODE_ECB).decrypt(block)
print(enc_step1)
enc_step2 = rc(enc_step1, password[0] % 256)
print(enc_step2)
enc_step3 = rb(enc_step2, 1)
print(enc_step3)
enc_step4 = rd(enc_step3)
print(enc_step4)
enc_step5 = ra(enc_step4, salt)

print(''.join(map(chr, enc_step5)))