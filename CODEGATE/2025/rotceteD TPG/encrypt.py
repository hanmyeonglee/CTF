import random
from glob import glob
from Crypto.Cipher import AES

flag = b"codegate2025{fake_flag}"

essays = []

for i in range(64):
    with open(f"gpt/{i:02}.txt") as f:
        essays.append((f.read(), 1))
    with open(f"qwen/{i:02}.txt") as f:
        essays.append((f.read(), 0))

random.shuffle(essays)

key = 0

for i in range(128):
    with open(f"essays/{i:03}.txt", 'w') as f:
        f.write(essays[i][0])
    key *= 2
    key += essays[i][1]

key = key.to_bytes(16, byteorder='big')
cipher = AES.new(key, AES.MODE_GCM)

nonce = cipher.nonce
ciphertext, tag = cipher.encrypt_and_digest(flag)

print(nonce.hex())
print(ciphertext.hex())
print(tag.hex())