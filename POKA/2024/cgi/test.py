import socket
result = ''
packet = """GET /ping HTTP/1.1
Host: host3.dreamhack.games:17297
Connection: keep-alive

"""

path, port = 'host3.dreamhack.games', 17297
try:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(5)
        s.connect((path, port))
        s.sendall(packet.encode())
        while True:
            tmp = s.recv(1024)
            result += tmp.decode()
            if not tmp: break
except Exception as e:
    print(e)

print(result)