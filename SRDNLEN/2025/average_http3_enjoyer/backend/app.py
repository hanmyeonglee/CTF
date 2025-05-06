from flask import Flask, request, render_template

app = Flask(__name__, static_url_path='/', static_folder='./static', template_folder='./templates')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/flag')
def flag():
    return "srdnlen{f4k3_fl4g}"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
