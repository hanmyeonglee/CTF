from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from hashlib import md5

a = 0.4336282047950153046404
ct = bytes.fromhex('7863c63a4bb2c782eb67f32928a1deceaee0259d096b192976615fba644558b2ef62e48740f7f28da587846a81697745')

def decrypt(n):
    return unpad(AES.new(
        md5(f"{int((n + a) ** 2)}".encode()).digest(),
        AES.MODE_ECB
    ).decrypt(ct), 16)

for n in range(10 ** 5, 10 ** 6):
    if ((n + a) ** 2).is_integer():
        try:
            pt = decrypt(n)
            if pt.startswith(b'uiu'):
                print(pt.decode())
        except:
            continue