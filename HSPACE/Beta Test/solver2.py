from base64 import b64encode, b64decode
from Crypto.Cipher import AES
from Crypto.Util.number import bytes_to_long, long_to_bytes
import string

def split_size_16(text: bytes) -> list[bytes]:
    ret = []
    for i in range(0, len(text), 16):
        ret.append(text[i:i+16])
    return ret

def a(x, y):
    ret = []
    for i in range(len(x)):
        res = (x[i]) ^ (y[i])
        ret.append(res)

    return ret


def b(x, y):
    ret = []
    for i in x:
        tmp = i
        tmp1 = tmp << y
        tmp2 = 8 - y
        tmp3 = tmp >> tmp2
        tmp4 = tmp1 | tmp3
        tmp5 = tmp4 & 255
        ret.append(tmp5)

    return ret


def c(x, y):
    ret = []
    for i in x:
        tmp = i
        res = (tmp + y) % 256
        ret.append(res)

    return ret


def d(x):
    ret = []
    for t in x:
        ct = chr(t)
        if ct.isalpha():
            tmp = t + 13
            if ct.isupper():
                if tmp > 90:
                    tmp += 65 - 91
            else:
                if tmp > 122:
                    tmp += 97 - 123
        else:
            tmp = t
        ret.append(tmp)

    return ret


def main(x, y, z, size=16):
    salt = z
    password = y
    flag = ''

    for i, block in enumerate(x):
        i *= 16
        print(i, block, password, salt, y, z)
        dec = AES.new(password, AES.MODE_ECB).decrypt(block)
        block_flag = ''

        for j in range(16):
            for ch in string.digits + string.ascii_lowercase + '{}' + string.ascii_uppercase + '_ ?!':
                tmp_flag = block_flag + ch

                after_a = a(tmp_flag.encode(), salt)
                after_d = d(after_a)
                after_b = b(after_d, i % 8 + 1)
                after_c = c(after_b, (y[i % len(y)] + i) % 256)

                if after_c[j] == dec[j]:
                    print(tmp_flag)
                    block_flag += ch
                    break
            else:
                raise Exception()
        
        res = AES.new(password, AES.MODE_ECB).encrypt(bytes(after_c))

        assert res == block

        salt = block
        password = block[:16]
        flag += block_flag

        print(i, block, password, salt, y, z)

    return flag


goal = b'vXR1VGYbvAEChVv+wQazyhyN9AXlTp2Kqoaz5Sm3FtxuJHJ+3BVRaeJ2PO+GmzZF'
password = b'd7mXTONUOhWIVHgy'
salt = b'buNj#7]0~!<ua:>\\\\'

enc_blocks = split_size_16(b64decode(goal))
total = ''

block = enc_blocks[0]
tmp_salt, tmp_password = salt, password
flag = ''
i = 0
dec = AES.new(tmp_password, AES.MODE_ECB).decrypt(block)
for j in range(16):
    for ch in string.digits + string.ascii_lowercase + '{}' + string.ascii_uppercase + '_ ?!':
        tmp_flag = flag + ch

        after_a = a(tmp_flag.encode(), tmp_salt)
        after_d = d(after_a)
        after_b = b(after_d, i % 8 + 1)
        after_c = c(after_b, (password[i % len(password)] + i) % 256)

        if after_c[j] == dec[j]:
            print(tmp_flag)
            flag += ch
            break
    else:
        raise Exception()
total += flag
print(total)
tmp_salt, tmp_password = block, block


block = enc_blocks[1]
flag = ''
for i in range(18):
    try:
        dec = AES.new(tmp_password, AES.MODE_ECB).decrypt(block)
        for j in range(16):
            for ch in string.digits + string.ascii_lowercase + '{}' + string.ascii_uppercase + '_ ?!':
                tmp_flag = flag + ch

                after_a = a(tmp_flag.encode(), tmp_salt)
                after_d = d(after_a)
                after_b = b(after_d, i % 8 + 1)
                after_c = c(after_b, (password[i % len(password)] + i) % 256)

                if after_c[j] == dec[j]:
                    print(tmp_flag)
                    flag += ch
                    break
            else:
                raise Exception()
    except:
        print(i)
        continue

    break
total += flag
print(total)
tmp_salt, tmp_password = block, block
