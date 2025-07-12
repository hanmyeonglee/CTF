from time import sleep

def rot47(s):
    return ''.join(
        chr(33 + ((ord(c) - 33 + 47) % 94)) if 33 <= ord(c) <= 126 else c
        for c in s
    )

i = 1337
j = 0

step = 3058
pool = '?o>`Wn0o0U0N?05o0ps}q0|mt`ne`us&400_pn0ss_mph_0`5'
pool = rot47(pool)
print(pool)
pool = "n3m1y2_3_w_pn_d3_47N5_MK812C197Uc__042_770K4F0_1d"

a = 86247
b = 86353 + 66
flag = ''
FLAG = "CTF{"

while True:
    j = ((i if i != 0 else 1) * 16807 + step) % 2147483647
    print(pool[j % len(pool)], end='')
    if step < 1000000:
        i = j
        pool = pool[: j % len(pool)] + pool[j % len(pool) + 1 :]
        #print(pool)
        step += b
        if len(pool) == 0: break
    else: break

    #sleep(0.5)

#print(FLAG + "}")