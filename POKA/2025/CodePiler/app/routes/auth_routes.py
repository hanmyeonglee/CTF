from flask import Blueprint, request, jsonify, session
import os

auth_bp = Blueprint('auth_bp', __name__)
from auth import login_required

def init_auth_routes(auth_manager):
    @auth_bp.route('/register', methods=['POST'])
    def register():
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        if not username or not password:
            return jsonify({"status": "error", "message": "Username and password are required."}), 400

        success, message = auth_manager.register(username, password)
        if success:
            user = auth_manager.login(username, password)
            user_dir = os.path.join('/app/users', user['id'])
            os.makedirs(user_dir, exist_ok=True)
            setting_file = os.path.join(user_dir, f".env")
    
            with open(setting_file, 'w', encoding='utf-8') as fp:
                fp.write(f'UNLOCK_KEY=' + user['key'] + '\n')

            return jsonify({"status": "success", "message": message})
        else:
            return jsonify({"status": "error", "message": message}), 400

    @auth_bp.route('/login', methods=['POST'])
    def login():
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        if not username or not password:
            return jsonify({"status": "error", "message": "Username and password are required."}), 400

        user = auth_manager.login(username, password)
        if user:
            session['key'] = user['key']
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['is_admin'] = user['is_admin']
            return jsonify({"status": "success", "message": "Logged in.", "user": {"username": user['username'], "is_admin": user['is_admin']}})
        else:
            return jsonify({"status": "error", "message": "Invalid credentials."}), 401

    @auth_bp.route('/logout', methods=['POST'])
    def logout():
        session.clear()
        return jsonify({"status": "success", "message": "Logged out."})

    @auth_bp.route('/promote', methods=['POST'])
    @login_required
    def promote():
        if not session.get('user_id'):
            return jsonify({"status": "error", "message": "You must be logged in to do this."}), 403
            
        data = request.get_json()
        secret = data.get('secret')

        success, message = auth_manager.promote_to_admin(session['user_id'], secret)
        if success:
            session['is_admin'] = True
            return jsonify({"status": "success", "message": message})
        else:
            return jsonify({"status": "error", "message": message}), 400
            
    return auth_bp
