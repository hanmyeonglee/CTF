from flask import Flask, request, redirect

app = Flask(__name__)

def print_in_flask(*args, **kwargs):
    with app.app_context():
        print(*args, **kwargs)

@app.route('/')
def index():
    print_in_flask(request.headers)
    return "Hello, World!"

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        return redirect('/')
    return '''
        <form method="post">
            Username: <input type="text" name="username"><br>
            Password: <input type="password" name="password"><br>
            <input type="submit" value="Login">
        </form>
    '''

app.run('0.0.0.0', port=12345)