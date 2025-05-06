import hashlib
import string
import random

user_id = "3"
prefix = "4ME27oeW"
difficulty = "000000"

charset = string.ascii_letters + string.digits

def find_nonce():
    attempts = 0
    while True:
        # 알파뉴메릭 nonce 생성 (길이는 필요에 따라 조정)
        nonce = ''.join(random.choices(charset, k=8))
        data = f"{user_id}:{prefix}:{nonce}"
        digest = hashlib.sha256(data.encode()).hexdigest()
        attempts += 1

        if digest.startswith(difficulty):
            print(f"[+] Found nonce: {nonce}")
            print(f"[+] SHA256({data}) = {digest}")
            print(f"[+] Attempts: {attempts}")
            return nonce

nonce = find_nonce()
print(f"Enter this nonce: {nonce}")