import hashlib

flag = 'hspace{}'
salt = int(flag.encode().hex(), 16)
number = int(input('Number: '))
print('Your Number:', number)
print('Hash:', hashlib.sha256(str(number + salt).encode()).hexdigest())