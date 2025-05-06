from Crypto.Util.number import long_to_bytes
from Crypto.Cipher import AES
from hashlib import sha256
import zlib, json

def xor(a: bytes, b: bytes) -> bytes:
	return bytes(x^y for x,y in zip(a,b))

def decrypt(key: bytes, iv: bytes, ciphertext: bytes):
    plaintext = b""
    ecb_cipher = AES.new(key=key, mode=AES.MODE_ECB)
    
    for pos in range(0, len(ciphertext), 16):
        chunk = ciphertext[pos:pos+16]
        
        # AES CFB for the last block or if there is only one block
        if len(ciphertext[pos+16:pos+32]) == 0 :
            
            #if plaintext length <= 16, iv = iv
            if len(ciphertext) <= 16 :
                prev=iv
            # else, iv = previous ciphertext
            else:
                prev=ciphertext[pos-16:pos]

            prev = ecb_cipher.encrypt(prev)
            plaintext += xor(prev, chunk)
            
        # AES CBC for the n-1 firsts block
        elif not plaintext:
            xored = ecb_cipher.decrypt(chunk)
            plaintext += bytes(xor(xored, iv))
            
        else:
            xored = ecb_cipher.decrypt(chunk)
            plaintext += bytes(xor(xored, ciphertext[pos-16:pos]))
            
    return plaintext

with open("my_zed/flag.txt.ozed", "rb") as ozed:
    enc = ozed.read()[4:]

metadata, enc = enc[:300], zlib.decompress(enc[300:])
metadata = metadata[:metadata.find(b'\x00')]
metadata = json.loads(metadata)
password = bytes.fromhex(metadata['password_hash'])[:16]
iv, ct = enc[:16], enc[16:]

flag = decrypt(password, iv, ct).decode()
print(f'{flag = }')