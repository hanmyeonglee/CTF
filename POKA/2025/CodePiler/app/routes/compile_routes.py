from flask import Blueprint, request, jsonify, session
import subprocess
import uuid
import os
from markitdown import MarkItDown
import hashlib

from auth import login_required, admin_required

compile_bp = Blueprint('compile_bp', __name__)

@compile_bp.route('/c', methods=['POST'])
@login_required
def compile_c():
    data = request.get_json()
    code = data.get('code')
    if not code:
        return jsonify({"status": "error", "message": "C code is required."}), 400
    if len(code) > 50000:
        return jsonify({"status": "error", "message": "C code is too long."}), 400

    user_dir = os.path.join('/app/users', session['user_id'])
    os.makedirs(user_dir, exist_ok=True)
    
    filename = str(uuid.uuid4())
    filepath = os.path.join(user_dir, filename)
    source_file = f"{filepath}.c"
    output_file = f"{filepath}.out"

    try:
        with open(source_file, "w") as f:
            f.write(code)

        command = ["/usr/bin/gcc", source_file, "-o", output_file]
        result = subprocess.run(command, capture_output=True, text=True, timeout=5)

        if result.returncode == 0:
            return jsonify({"status": "success", "message": "Success", "output": 'good', 'filepath': filepath, 'error': result.returncode})
        else:
            return jsonify({"status": "error", "message": "Fail", "output": hashlib.sha256(result.stderr.encode()).hexdigest(), 'filepath': filepath, 'error': result.returncode})

    except subprocess.TimeoutExpired:
        return jsonify({"status": "error", "message": "Compilation timed out."}), 408
    except Exception:
        return jsonify({"status": "error", "message": "Error"}), 500


@compile_bp.route('/java', methods=['POST'])
@login_required
def execute_java():
    # TODO: Implement secure JAVA code execution (e.g., using a sandboxed environment)
    return jsonify({"status": "pending", "message": "JAVA compiler is not implemented yet."})


@compile_bp.route('/markdown', methods=['POST'])
@admin_required
def render_markdown():
    data = request.get_json()
    source_content = str(data.get('code'))
    source_url = str(data.get('url'))
    key = str(data.get('key'))

    if not source_content and not source_url:
        return jsonify({"status": "error", "message": "Markdown 'code' or 'url' is required."}), 400
    
    if key != session['key']:
        return jsonify({"status": "error", "message": "Not a valid key."}), 400

    source = source_url if source_url else source_content

    try:
        md = MarkItDown(enable_plugins=False)

        if not source_url:
            user_dir = os.path.join('/app/users', session['user_id'])
            os.makedirs(user_dir, exist_ok=True)
            temp_md_file = os.path.join(user_dir, f"{uuid.uuid4()}.md")
            with open(temp_md_file, "w") as f:
                f.write(source_content)
            source = temp_md_file

        result_html = md.convert(source).text_content

        if not source_url and os.path.exists(source):
            os.remove(source)

        return jsonify({"status": "success", "message": "Markdown rendered successfully.", "output": result_html})

    except Exception:
        return jsonify({"status": "error", "message": f"Error"}), 500
