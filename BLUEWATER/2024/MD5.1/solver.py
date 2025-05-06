from main import md5
from Crypto.Util.number import long_to_bytes
import os

key = [(long_to_bytes(x), long_to_bytes(0x80 ^ x)) for x in range(0, 256)]
i = 0

while i < 10:
    prefix = os.urandom(35)
    suffix = os.urandom(92)
    for x, y in key:
        msg1 = prefix + x + suffix
        msg2 = prefix + y + suffix
        if md5(msg1) == md5(msg2):
            result = f'msg1 = {msg1.hex()}\n' + \
                   + f'msg2 = {msg2.hex()}\n\n'
            print(result, file=(f := open('./result.txt', 'a', encoding='utf-8')), flush=True)
            f.close()
            i += 1

