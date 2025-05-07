import requests, time

PATH = 'https://hacktheon-api.ctf-zone.com'
for h in 5, 17:
    for m in range(60):
        res = requests.post(
            PATH + '/api/challenge/auth',
            headers={
                'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzQ1NjY5MDI3LCJpYXQiOjE3NDU2MjU4MjcsImp0aSI6ImY0ZjA4MzNiYjBlZTRmZWJiMTIxNjljNzBjNDY3ZGFlIiwidXNlcl9pZCI6MzA3N30.YAZcbmE2GSVLpug8Vq2Zp8ujewOHCokEKwCfjScmnnY',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36'
            },
            json={
                'flag': "FLAG{" + "2025/03/06_{:02d}:{:02d}".format(h, m) + "}",
                'id': 3
            }
        ).json()
        print(h, m, res)
        time.sleep(3)