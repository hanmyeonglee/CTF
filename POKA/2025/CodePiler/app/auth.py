import os

from functools import wraps
from flask import session, jsonify

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({"status": "error", "message": "Authentication required. Please log in."}), 401
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({"status": "error", "message": "Authentication required. Please log in."}), 401
        if not session.get('is_admin'):
            return jsonify({"status": "error", "message": "Admin privileges required."}), 403
        return f(*args, **kwargs)
    return decorated_function


class AuthManager:
    def __init__(self, secret_file_path):
        self.users = {}
        self.secret_file_path = secret_file_path

    @property
    def admin_secret(self):
        with open(self.secret_file_path, 'r', encoding='utf-8') as fp:
            secret_code = fp.read()
            return secret_code

    @staticmethod
    def generate_user_id():
        return os.urandom(8).hex()

    def register(self, username, password):
        if username in [user['username'] for user in self.users.values()]:
            return False, "Username already exists."
        
        user_id = AuthManager.generate_user_id()
        self.users[user_id] = {
            "id": user_id,
            "key": os.urandom(128).hex(),
            "username": username,
            "password": password,
            "is_admin": False,
            'try': 0
        }
        return True, "User registered successfully."

    def login(self, username, password):
        for user in self.users.values():
            if user['username'] == username and user['password'] == password:
                return user
        return None

    def promote_to_admin(self, user_id, secret):
        if user_id not in self.users:
            return False, "User not found."
        
        if self.users[user_id]['try'] > 5:
            return False, "Try next time...."
        self.users[user_id]['try'] += 1
        
        if secret == self.admin_secret:
            self.users[user_id]['is_admin'] = True
            return True, "Congratulations! You have been promoted to an admin."
        else:
            return False, "Incorrect secret code."

    def reset(self):
        self.users.clear()