from collections import Counter
from Crypto.Cipher import AES
import json

def main01():
    res = []
    for i in range(128):
        path = f'./essays/{i:03}.txt'
        with open(path, encoding='utf-8') as f:
            res.extend(f.read().split())

    json.dump(dict(sorted(Counter(res).items(), key=lambda x: (x[1], x[0]), reverse=True)), ensure_ascii=False, indent=1, fp=open('result.json', 'w', encoding='utf-8'))

def main02():
    res = []
    for i in range(128):
        path = f'./essays/{i:03}.txt'
        with open(path, encoding='utf-8') as f:
            res.extend(list(set(f.read().split())))

    json.dump(dict(sorted(Counter(res).items(), key=lambda x: (x[1], x[0]), reverse=True)), ensure_ascii=False, indent=1, fp=open('result.json', 'w', encoding='utf-8'))

def decrypt():
    key = ''
    for i in range(128):
        path = f'./essays/{i:03}.txt'
        with open(path, encoding='utf-8') as f:
            data = set(f.read().split())
            if 'like' in data:
                key += '0'
            else:
                key += '1'

    key = int(key, 2).to_bytes(16, byteorder='big')
    ct = bytes.fromhex('c88f0e97fbe289c7800a68c2aae64a1825e0405cca87f6360e5f194e43978e1772f09a5bd2812cf9db8cf9008be7e34222ed9ee22bf6188358a49ada4e6d5ae16e71b0807d414f')
    nonce = bytes.fromhex('3d6b85f9299442b2219a44aee1345e16')
    tag = bytes.fromhex('c58e546b2fed995d0a6a723c8f10f6d1')
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    pt = cipher.decrypt_and_verify(ciphertext=ct, received_mac_tag=tag)
            
    print(pt)

main01()