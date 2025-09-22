from flask import Flask
import sys
import os
import threading

from auth import AuthManager
from routes.auth_routes import init_auth_routes
from routes.compile_routes import compile_bp as compile_blueprint
from routes.settings_routes import settings_bp as settings_blueprint

BACKUP_ENVIRON = os.environ.copy()

app = Flask(__name__)
app.secret_key = os.urandom(24)

secret_file_path = sys.argv[1]
print(open(secret_file_path, 'r').read(), file=sys.stderr, flush=True)
auth_manager = AuthManager(secret_file_path)
auth_blueprint = init_auth_routes(auth_manager)

app.register_blueprint(auth_blueprint, url_prefix='/api/auth')
app.register_blueprint(compile_blueprint, url_prefix='/api/compile')
app.register_blueprint(settings_blueprint, url_prefix='/api/settings')

@app.route('/')
def index():
    return open('/app/templates/index.html', 'r', encoding='utf-8').read()

def clear_user_file():
    os.system('rm -rf /app/users/*')

def backup_env(backup):
    os.environ.clear()
    os.environ.update(backup)

def run_task():
    clear_user_file()
    backup_env(BACKUP_ENVIRON)
    auth_manager.reset()
    threading.Timer(600, run_task).start()

if __name__ == '__main__':
    run_task()
    app.run(host='0.0.0.0', port=5000, debug=False)

