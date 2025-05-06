import requests
from time import sleep

path = 'https://2025.irisc.tf/api'
headers = {
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    'Cookie': "PHPSESSID=imrb8v2i87no4v69m8er3ste5d; verpref=wgl"
}

# 39.8921 ~ 39.8941, 116.4999 ~ 116.5019
# 39.8921, 116.4965
# 39.8951, 116.5027

startX, startY = 39.890, 116.490

for i in range(11):
    for j in range(21):
        while True:
            flag = 'irisctf{' + f'{(startX + i * 0.001):.3f}_{(startY + j * 0.001):.3f}' + '}'
            print(f'{flag = }')

            res = requests.post(
                path,
                headers=headers,
                data={
                    'action': "submit_flag",
                    'challenge': 44,
                    'xsrf_token': "9494c32f12804bc073b0a22f2d748a2fd3b15ecb5155b12f60df117de64b71ef",
                    'flag': flag
                }
            )

            if 'Incorrect' in res.text: break
            if 'seconds' in res.text:
                sleep(5)
                continue
            print(res.text, file=open('result.txt', 'a'), flush=True)
            break
        sleep(5)