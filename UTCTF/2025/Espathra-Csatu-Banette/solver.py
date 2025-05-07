from pwn import remote
from Crypto.Util.number import long_to_bytes
import string

mx = 127
printable = {ch : long_to_bytes(ch) for ch in range(1, 128) if ch != 0x0a}

def get_16_multi(n: int) -> int:
    return 16 * ((n + 15) // 16)

def split_by_16(enc: bytes) -> list[bytes]:
    return [enc[i:i+16] for i in range(0, len(enc), 16)]

def one_cycle(program: remote, payload: bytes) -> bytes:
    program.recvuntil(b'encrypted: ')
    program.sendline(payload)
    ret = program.recvline(keepends=False).replace(b'0x', b'')
    return ret.zfill(len(ret) + len(ret) % 2)

def appropriate_payload(payload: bytes, goal: int) -> bytes:
    for ch in (printable.values()):
        chksum = sum(payload + ch) % (goal + 1)
        if chksum == goal: return payload + ch
    
    raise Exception("FUCK")

def get_flag_length(program: remote) -> int:
    prev_length = len(one_cycle(program, b'')) // 2
    for length in range(1, 16):
        payload = printable[mx] * (length - 1)
        payload = appropriate_payload(payload, length)
        current_length = len(one_cycle(program, payload)) // 2
        print(length, prev_length, current_length, payload)
        if prev_length < current_length:
            return prev_length - length
    
    raise Exception("FUCK22")

path, port = 'challenge.utctf.live', 7150
program = remote(path, port)

flag_length = 38# = get_flag_length(program)

print(f'flag length is {flag_length}')

flag = b't0!!}'
for _ in range(flag_length):
    unknown_length = flag_length - len(flag)
    isE = True
    for ch in string.printable:
        if ch == '\n': continue

        if len(flag) == 5:
            if ch != 'C' and isE: continue
            isE = False
            FLAG = ch.encode() + flag
            isfind = False
            isExist = True
            for ch2 in string.printable:
                if ch2 == '\n' : continue
                if ch == 'C' and ch2 != 't' and isExist: continue
                isExist = False
                payload = ch2.encode()
                payload += FLAG
                print('flag =', (ch2.encode() + FLAG).decode())

                payload += long_to_bytes(0x9) * 0x9

                payload += printable[mx] * (get_16_multi(unknown_length) - unknown_length)
                payload = appropriate_payload(payload, len(payload) + 1)
                chksum = sum(payload) % (len(payload) + 1)

                enc = split_by_16(bytes.fromhex(one_cycle(program, payload).decode()))
                index = -(len(FLAG) // 16 + 1)

                if enc[0] == enc[index]:
                    flag = ch2.encode() + FLAG
                    isfind = True
                    break
            
            if isfind: break
            continue

        payload = ch.encode()
        payload += flag
        print('flag =', (ch.encode() + flag).decode())

        if len(flag) < 16:
            pad = 16 - len(payload)
            payload += long_to_bytes(pad) * pad
        
        payload += printable[mx] * (get_16_multi(unknown_length) - unknown_length)
        payload = appropriate_payload(payload, len(payload) + 1)

        enc = split_by_16(bytes.fromhex(one_cycle(program, payload).decode()))
        index = -(len(flag) // 16 + 1)

        if enc[0] == enc[index]:
            flag = ch.encode() + flag
            break

    else:
        raise Exception("FUCK333")

print(flag)