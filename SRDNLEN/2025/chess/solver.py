def xorshift128(state0, state1):
    s1 = state0
    s0 = state1
    state0 = s0
    s1 ^= s1 << 23 
    s1 &= 0xFFFFFFFFFFFFFFFF
    s1 ^= s1 >> 17
    s1 ^= s0
    s1 ^= s0 >> 26
    state1 = s1
    return state0 & 0xFFFFFFFFFFFFFFFF, state1 & 0xFFFFFFFFFFFFFFFF

