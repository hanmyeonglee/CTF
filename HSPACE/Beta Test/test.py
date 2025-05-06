from Crypto.Cipher import AES
from base64 import b64encode, b64decode

a = AES.new(b'd7mXTONUOhWIVHgy', AES.MODE_ECB).encrypt(b'ffffffffffffffff')
print(b64encode(a))