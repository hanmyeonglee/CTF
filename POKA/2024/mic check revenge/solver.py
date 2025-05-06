from hashlib import sha1
import string
from itertools import product

result = '7d36b2c6e1c5f4ade132f744ceb9d40e3bd5291b'

target = string.ascii_lowercase + string.ascii_uppercase + string.digits

for flag in product(target, repeat=4):
    real_flag = ('pokactf2024{' + ''.join(flag) + '}').encode()
    if sha1(real_flag).hexdigest() == result:
        print(real_flag)
        exit()