from sage.all import *  
import os, pickle, binascii
from Crypto.Hash import SHA256

from OSIDH_implement import OSIDH, Chain, Chain_hor
N = 28      
T = 10      
L = 2       
R = 3       
D_K = -4    

def kdf_from_j(j):
    return SHA256.new(str(j).encode()).digest()

def xor_bytes(a: bytes, b: bytes) -> bytes:
    n = min(len(a), len(b))
    return bytes(x ^ y for x, y in zip(a[:n], b[:n]))

osidh = OSIDH(N, T, L, R, D_K)              
pub_chain = Chain(osidh)                      

exit(0)

L_exp_A = [randint(-osidh.r, osidh.r) for _ in range(osidh.t)]
L_exp_B = [randint(-osidh.r, osidh.r) for _ in range(osidh.t)]

chain_A = pub_chain.action(L_exp_A)           
chain_B = pub_chain.action(L_exp_B)

A_hor = []
B_hor = []
for j in range(osidh.t):

    # Alice’s horizontals
    ch = chain_A
    L_plus = []
    for _ in range(osidh.r):
        ch = ch.action_prime(osidh.L_mfq[j], j)
        L_plus.append(ch.L_j[-1])
    ch = chain_A
    L_minus = []
    for _ in range(osidh.r):
        ch = ch.action_prime(osidh.L_mfq_inv[j], j)
        L_minus.append(ch.L_j[-1])
    A_hor.append(Chain_hor(osidh, j, chain_A.L_j[-1], L_plus, L_minus))

    # Bob’s horizontals
    ch = chain_B
    L_plus = []
    for _ in range(osidh.r):
        ch = ch.action_prime(osidh.L_mfq[j], j)
        L_plus.append(ch.L_j[-1])
    ch = chain_B
    L_minus = []
    for _ in range(osidh.r):
        ch = ch.action_prime(osidh.L_mfq_inv[j], j)
        L_minus.append(ch.L_j[-1])
    B_hor.append(Chain_hor(osidh, j, chain_B.L_j[-1], L_plus, L_minus))

shared_j = chain_B.action(L_exp_A).L_j[-1]

FLAG_PATH = os.environ.get("FLAG_PATH", "flag.txt")
flag = open(FLAG_PATH, "rb").read().strip()

key = kdf_from_j(shared_j)
ct = xor_bytes(flag, key)

with open("osidh.pkl", "wb") as f:
    pickle.dump(osidh, f)
with open("pub_chain.pkl", "wb") as f:
    pickle.dump(pub_chain, f)
with open("A_hor.pkl", "wb") as f:
    pickle.dump(A_hor, f)
with open("B_hor.pkl", "wb") as f:
    pickle.dump(B_hor, f)
with open("flag.enc", "w") as f:
    f.write(binascii.hexlify(ct).decode())
