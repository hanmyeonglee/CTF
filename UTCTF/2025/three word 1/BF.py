import requests, json, time

path = 'https://utctf.live/api/v1/challenges/attempt'
words = json.load(fp=open('words.json'))
headers = {
    "Accept": "application/json",
    "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
    "Cache-Control": "no-cache",
    "Content-Length": "62",
    "Content-Type": "application/json",
    "Cookie": "session=13c1744d-feef-4db3-8de4-7aa3ef87a924.XXsaxDax6gIat78B6IPyf7js_Ec",
    "Csrf-Token": "91e509e674941681cde2020d74165a513be6623821a58c4ee612fe6fc86f0138",
    "Origin": "https://utctf.live",
    "Pragma": "no-cache",
    "Priority": "u=1, i",
    "Referer": "https://utctf.live/challenges",
    "Sec-Ch-Ua": '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"Windows"',
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"
}

for i, word in enumerate(words):
    print(i+1, 'utflag{'+word+'}', end=' ')
    
    res = requests.post(
        path,
        headers=headers,
        json={
            'challenge_id': 4,
            'submission': 'utflag{'+word+'}'
        }
    )

    print(res, res.text)

    time.sleep(5)