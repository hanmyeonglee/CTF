from flask import Flask, render_template, redirect, request, url_for, redirect, jsonify
import os
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
from flask_bcrypt import Bcrypt
from bot import *
from urllib.parse import *
import pymysql

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_USER = os.getenv("DB_USER", "poka")
DB_PASSWORD = os.getenv("DB_PASSWORD", "poka")
DB_NAME = os.getenv("DB_NAME", "prob_csp")

conn = pymysql.connect(
    host=DB_HOST, user=DB_USER, password=DB_PASSWORD, db=DB_NAME, port=DB_PORT,
    cursorclass=pymysql.cursors.DictCursor
)

app = Flask(__name__)
app.secret_key = os.urandom(24)
bcrypt = Bcrypt(app)

@app.after_request
def apply_csp(response):
    token = request.args.get('token', '')
    response.headers['Content-Security-Policy'] = (
        "object-src 'none'; "
        "script-src 'self'; "
        "style-src 'self'; "
        f"report-uri /csp-report?token={token}"
    )
    return response

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, id, username, email):
        self.id = id
        self.username = username
        self.email = email

@login_manager.user_loader
def load_user(user_id):
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM users WHERE id=%s", (int(user_id),))
        row = cursor.fetchone()
    if not row:
        return None
    return User(row['id'], row['username'], row['email'])


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/user')
@login_required
def api_user():
    return jsonify({
        'username': current_user.username,
        'email':    current_user.email,
    })

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        password_confirm = request.form['password_confirm']
        if password != password_confirm:
            return 'Passwords do not match'
        
        password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

        with conn.cursor() as cursor:
            try:
                cursor.execute(
                    "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
                    (username, email, password_hash)
                )
                conn.commit()
            except pymysql.err.IntegrityError:
                return 'Username already exists'
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
            user = cursor.fetchone()

            if user and bcrypt.check_password_hash(user['password'], password):
                user = User(user['id'], user['username'], user['email'])
                login_user(user)
                return redirect(url_for('index'))
            else:
                return "아이디 또는 비밀번호가 잘못되었습니다."
    return render_template('login.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/mypage')
@login_required
def mypage():
    return render_template('mypage.html')

@app.route('/mypage_modify', methods=['GET', 'POST'])
@login_required
def mypage_modify():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']

        with conn.cursor() as cursor:
            cursor.execute(
                "UPDATE users SET username=%s, email=%s WHERE id=%s",
                (username, email, current_user.id)
            )
            conn.commit()
        return redirect(url_for('mypage'))
    
    data = request.args.to_dict()
    show_popup = bool(data)
    return render_template('mypage_modify.html', data=data, show_popup=show_popup)

@app.route("/report", methods=["GET", "POST"])
def report():
    if request.method == "GET":
        return render_template("report.html")
    bot = Bot()
    url = request.form.get('report_url')
    if url:
        try:
            parsed_url = urlparse(url)
        except Exception:
            return {"error": "Invalid URL."}, 400

        if parsed_url.scheme not in ["http", "https"]:
            return {"error": "Invalid scheme."}, 400

        bot.visit(url)
        bot.close()
        return {"visited": url}, 200
    else:
        return {"error": "URL parameter is missing!"}, 400
    
@app.route("/csp-report", methods=["POST"])
def csp_report():
    # this page is under construction
    return "", 204

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=7575)
