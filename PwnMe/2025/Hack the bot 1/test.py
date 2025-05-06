import base64, string
from itertools import permutations

for ls in permutations(string.ascii_lowercase, 4):
    t = ''.join(ls).encode()
    if b'T' in base64.b64encode(t):
        print(t, base64.b64encode(t))
        input()
    
    for i in range(3):
        try:
            if b'T' in base64.b64decode(t):
                print(t, base64.b64decode(t))
                input()
        except:
            t += '='
            continue
        break