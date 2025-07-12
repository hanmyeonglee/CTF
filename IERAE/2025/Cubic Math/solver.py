#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
exploit.py – 자동으로 g_i 세트 수집 → secret 복원 → FLAG 획득
author : you
usage  : python3 exploit.py HOST PORT
"""
from pwn import *
from random import randrange
from sympy import nextprime, isprime

CTX = context
CTX.terminal = ["tmux", "splitw", "-h"]
CTX.log_level = "info"

#HOST, PORT = sys.argv[1], int(sys.argv[2])

# ────────────────────────────── 1. g_i 전체 수집 ──────────────────────────────
def collect_gaps(io):
    """
    50 번 질의 안에서 10 개의 g_i(= p_i − secret) 모두 수집한다.
    (x³ + ax + b)가 irreducible일 확률이 ≈ 2/3 이므로
    a, b 를 난수로만 던져도 평균 15 회 내에 complete set 확보 가능.
    """
    gaps = set()
    for _ in range(50):
        a = randrange(-2**31, 2**31)
        b = randrange(-2**31, 2**31)
        io.recvuntil(b"a, b = ")
        io.sendline(f"{a},{b}".encode())
        line = io.readline().decode().strip()
        # server.py 는 결과를 파이썬 list 형식으로 출력
        try:
            res = eval(line)
        except Exception:
            log.failure(f"unexpected line: {line}")
            exit()
        gaps.update(res)
        log.info(f"now have {len(gaps)}/10 gaps")

        if len(gaps) == 10:
            break
    else:
        log.failure("didn't get all 10 gaps within 50 queries!")
        exit()

    return sorted(gaps)

# ─────────────────────── 2. gap signature → secret 복원 ───────────────────────
def recover_secret(gaps, search_bits=64):
    """
    gap 시퀀스는 256-bit 공간에서도 사실상 '지문' 수준으로 유일.
    현실적으로는 CTF 측이 secret 범위를 2**search_bits 이하로
    낮춰 두었을 가능성이 높으므로 (default 64 bit) 그 안에서 탐색.

    아이디어
    --------
      * g[0] ≤ ln(secret) 수준이므로 매우 작다.
      * primes = [s+g[0], s+g[1], …, s+g[9]] 가 **연속 10개 소수**여야 함.
      * 따라서 어떤 후보 p₀ 가 소수이고, 그 다음 9 개의
        nextprime 연산을 돌렸을 때 정확히 같은 gap 패턴이 나오면
        secret = p₀ − g[0].

    brute-force 함수 `scan(start, end)` 는 이러한 p₀ 를 찾는다.
    """
    d_seq = tuple(g2 - g1 for g1, g2 in zip(gaps, gaps[1:]))  # gap differences

    def scan(start, end):
        x = nextprime(start - 1)
        while x <= end:
            ok = True
            y = x
            for d in d_seq:
                y = nextprime(y + 1)
                if y - x != gaps[gaps.index(0) if 0 in gaps else 0] + sum(d_seq[:d_seq.index(d)+1]):
                    ok = False
                    break
            if ok:
                return x
            x = nextprime(x + 1)
        return None

    log.info("searching candidate prime sequence …")
    upper = 1 << search_bits
    p0 = scan(3, upper)
    if p0 is None:
        log.failure("secret not found in given range; raise search_bits")
        exit()

    secret = p0 - gaps[0]  # g[0] is the first difference
    log.success(f"secret recovered: {secret}")
    return secret

# ────────────────────────────── 3. 최종 FLAG 획득 ─────────────────────────────
def get_flag(io, secret):
    """
    server.py 는 a == secret 일 때 곧장 FLAG 를 출력하고 return:contentReference[oaicite:0]{index=0}
    (32-bit 범위 체크보다 먼저 비교). 따라서 마지막 1 회만 맞추면 된다.
    """
    io.recvuntil(b"a, b = ")
    io.sendline(f"{secret},0".encode())
    flag = io.readline().decode().strip()
    if flag.startswith("CTF"):
        log.success(f"FLAG ⇒ {flag}")
    else:
        log.failure(f"unexpected output: {flag}")

# ────────────────────────────────── main ─────────────────────────────────────
def main():
    #io = remote(HOST, PORT)
    io = process(['python3', 'distfiles/server.py'])
    gaps = collect_gaps(io)
    secret = recover_secret(gaps)
    get_flag(io, secret)

if __name__ == "__main__":
    main()
