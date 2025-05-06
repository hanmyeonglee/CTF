from flask import Flask, request, render_template
import socket
import os

app = Flask(__name__, static_folder='./static/css/')
app.secret_key = os.urandom(32)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ping', methods=['GET', 'POST'])
def ping():
    if request.method == 'GET':
        return render_template('ping.html', message = 'host=&port=&message=')
    elif request.method == 'POST':
        host = request.form.get('host')
        port = request.form.get('port', 80, type=int)
        packet = request.form.get('packet')
        result = ""

        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(5)
                s.connect((host, port))
                s.sendall(packet.encode())
                while True:
                    tmp = s.recv(1024)
                    result += tmp.decode()
                    if not tmp: break
            
        except Exception as e:
            return render_template('ping.html', message=str(e))
        
        return render_template('ping.html', message=str(result))

app.run('0.0.0.0', 8080)
