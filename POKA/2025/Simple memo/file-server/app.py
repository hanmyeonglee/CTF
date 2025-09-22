from flask import Flask, request, send_from_directory, make_response, abort
import os

app = Flask(__name__)

app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024

UPLOAD_DIR = "./uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

disable_ext = ['.htm', '.xhtml','.shtml','.asp','.jsp','.svg', '.xml','.xht']

def check_ext(filename):
    fname = filename.lower()
    for ext in disable_ext:
        if fname.endswith(ext):
            return False
    return True

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return "No file part", 400
    file = request.files['file']
    with app.app_context():
        print(file.filename)
    if file.filename == '':
        return "No selected file", 400
    if not check_ext(file.filename):
        return "Forbbiden ext", 400
        
    filepath = os.path.join(UPLOAD_DIR, file.filename)
    file.save(filepath)
    return f"File uploaded: {file.filename}", 200

@app.route('/uploads/<path:filename>')
def serve_file(filename):
    filepath = os.path.join(UPLOAD_DIR, filename)
    if not os.path.isfile(filepath):
        abort(404)

    response = make_response(send_from_directory(UPLOAD_DIR, filename))
    response.headers['X-Content-Type-Options'] = 'nosniff'
    return response

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
