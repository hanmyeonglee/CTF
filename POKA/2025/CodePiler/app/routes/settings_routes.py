from flask import Blueprint, request, jsonify, session
import os
from dotenv import load_dotenv
import re

from auth import login_required, admin_required

settings_bp = Blueprint('settings_bp', __name__)

VALID_KEY = r"[a-zA-Z0-9_]{1,80}"
VALID_VALUE = r"[^\x00-\x20\x80-\xff]{1,80}"
ALLOWED_ENV_KEYS = ['dummy1', 'dummy2', 'dummy3'] # hihi
DANGEROUS_ENVS = [
    'HOSTNAME','HOME','GPG_KEY','PYTHON_SHA256','TERM','PATH','LANG','PYTHON_VERSION','PWD', 'PYTHONPATH', 'LD_LIBRARY_PATH'
]

@settings_bp.route('/setenv', methods=['POST'])
@admin_required
def setenv():
    data = request.get_json()
    key = str(data.get('key')).strip()
    value = str(data.get('value')).strip()
    add_front = bool(data.get('add_front', True))

    if not key or not value:
        return jsonify({"status": "error", "message": "'key' and 'value' is required."}), 400
    if not re.fullmatch(VALID_KEY, key):
        return jsonify({"status": "error", "message": "Not a valid 'key'"}), 400
    if not re.fullmatch(VALID_VALUE, value):
        return jsonify({"status": "error", "message": "Not a valid 'value'"}), 400
    
    for danger in DANGEROUS_ENVS:
        if danger == key:
            return jsonify({"status": "error", "message": "Dangerous key."}), 400

    try:
        user_dir = os.path.join('/app/users', session['user_id'])
        setting_file = os.path.join(user_dir, f".env")
        setting_file_content = open(setting_file, 'r', encoding='utf-8').read()

        if len(setting_file_content) > 500:
            return jsonify({"status": "error", "message": "Too long."}), 400

        new_content = f'{key}={value}'
        
        for kev_value in map(lambda x:x.split('='), setting_file_content.split('\n')):
            if kev_value[0] == key:
                raise Exception('Overwrite is not allowed')

        with open(setting_file, 'w', encoding='utf-8') as fp:
            if add_front:
                fp.write(new_content + '\n' + setting_file_content)
            else:
                fp.write(setting_file_content + '\n' + new_content + '\n')

        load_dotenv(setting_file)

        return jsonify({"status": "success", "message": "Success", "output": ''})

    except Exception:
        return jsonify({"status": "error", "message": f"Error"}), 500

@settings_bp.route('/getenv', methods=['GET'])
@admin_required
def getenv():
    key = request.args.get('key')

    if not key:
        return jsonify({
            "status": "error",
            "message": "Query parameter 'key' is required."
        }), 400

    if key in ALLOWED_ENV_KEYS:
        value = os.environ.get(key)
        if value is not None:
            return jsonify({
                "status": "success",
                "data": {key: value}
            })
        else:
            return jsonify({
                "status": "error",
                "message": f"Environment variable '{key}' not found."
            }), 404
    else:
        return jsonify({
            "status": "error",
            "message": f"Access to the environment variable '{key}' is forbidden."
        }), 403
