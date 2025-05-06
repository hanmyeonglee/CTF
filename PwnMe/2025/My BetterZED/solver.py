from Crypto.Protocol.KDF import PBKDF2
from Crypto.Hash import SHA256
from hashlib import sha256

password = b'password'
salt = b'LESELFRANCAIS!!!'
res1 = PBKDF2(password, salt, dkLen=16, count=10000, hmac_hash_module=SHA256)
assert SHA256.new(password).hexdigest() == sha256(password).hexdigest()
res2 = PBKDF2(SHA256.new(password).hexdigest(), salt, dkLen=16, count=9999, hmac_hash_module=SHA256)

print(res1)
print(res2)