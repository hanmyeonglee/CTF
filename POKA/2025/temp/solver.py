# mitm_ascii.py
# Run: sage -python mitm_ascii.py --workers 12 --meet 5
import argparse, pickle, binascii, time, sys
from multiprocessing import Process, Manager, cpu_count
from Crypto.Hash import SHA256
from sage.all import *
from OSIDH_implement import Action_hor

def kdf_from_j(j):
    return SHA256.new(str(j).encode()).digest()

def xor_bytes(a: bytes, b: bytes) -> bytes:
    n = min(len(a), len(b))
    return bytes(x ^ y for x, y in zip(a[:n], b[:n]))

def int_to_vec7(x, length, r):
    v = [0]*length
    for i in range(length):
        d = x % 7
        x //= 7
        v[i] = d - r
    return v

def is_ascii_readable(bs: bytes):
    # treat as valid only if ALL bytes are printable ASCII (space..~)
    return len(bs) > 0 and all(32 <= b <= 126 for b in bs)

def build_left_prefixes(osidh, B_hor, m, r):
    total = 7**m
    L1_list = []
    t0 = time.time()
    for x in range(total):
        L1_list.append(tuple(int_to_vec7(x, m, r)))
        if (x+1) % 2000 == 0:
            print(f"[left] {x+1}/{total} built in {time.time()-t0:.1f}s")
    return L1_list

def worker_right(worker_id, start, end, m, tlen, r, L1_list, osidh, B_hor, ct, shared):
    checked = 0
    t0 = time.time()
    for rid in range(start, end):
        if shared['found']:
            return
        R = int_to_vec7(rid, tlen - m, r)
        for L1 in L1_list:
            L_full = list(L1) + list(R)
            try:
                final_j = Action_hor(osidh, B_hor, L_full)
            except Exception:
                continue
            plain = xor_bytes(ct, kdf_from_j(final_j))
            checked += 1
            if checked % 20000 == 0:
                print(f"[W{worker_id}] {checked} checked (rid {rid}) elapsed {time.time()-t0:.1f}s")
            if is_ascii_readable(plain):
                shared['found'] = True
                shared['result'] = {
                    'worker': worker_id,
                    'L_full': L_full,
                    'plain': plain
                }
                with open(f"found_plain_worker{worker_id}.bin","wb") as f:
                    f.write(plain)
                print(f"[W{worker_id}] ASCII-readable FLAG found with L_full={L_full}")
                return
    print(f"[W{worker_id}] done; checked {checked} candidates in {time.time()-t0:.1f}s")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--meet", type=int, default=5)
    ap.add_argument("--workers", type=int, default=max(1, cpu_count()-15))
    args = ap.parse_args()

    with open("osidh.pkl","rb") as f: osidh = pickle.load(f)
    with open("pub_chain.pkl","rb") as f: pub_chain = pickle.load(f)
    with open("A_hor.pkl","rb") as f: A_hor = pickle.load(f)
    with open("B_hor.pkl","rb") as f: B_hor = pickle.load(f)
    ct_hex = open("flag.enc","r").read().strip()
    ct = binascii.unhexlify(ct_hex)

    m = args.meet
    tlen = osidh.t
    r = osidh.r
    assert 0 < m < tlen

    print(f"[+] params: t={tlen}, r={r}, meet={m}, workers={args.workers}")
    print("[+] Building left prefixes…")
    L1_list = build_left_prefixes(osidh, B_hor, m, r)

    total_right = 7**(tlen - m)
    chunk = (total_right + args.workers - 1) // args.workers

    manager = Manager()
    shared = manager.dict()
    shared['found'] = False
    shared['result'] = None

    procs = []
    for w in range(args.workers):
        start = w*chunk
        end = min(total_right, (w+1)*chunk)
        p = Process(target=worker_right,
                    args=(w, start, end, m, tlen, r, L1_list, osidh, B_hor, ct, shared))
        p.start()
        procs.append(p)

    try:
        while True:
            time.sleep(2)
            if shared['found']: break
            if not any(p.is_alive() for p in procs): break
    except KeyboardInterrupt:
        pass
    finally:
        for p in procs:
            try: p.terminate()
            except: pass
        for p in procs:
            p.join(timeout=1)

    if shared['found']:
        res = dict(shared['result'])
        print("[=== RESULT ===]")
        print("worker:", res['worker'])
        print("L_full:", res['L_full'])
        print("plaintext:", res['plain'])
        print("Saved to found_plain_worker%d.bin" % res['worker'])
    else:
        print("No ASCII-readable plaintext found.")

if __name__ == "__main__":
    main()
