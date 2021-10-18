from flask import Flask
from auth.views import auth

app = Flask(__name__)

app.secret_key = "SECRETE TEST"

app.register_blueprint(auth)


@app.route('/')
def hello_world():
    return 'Hello World!'

@app.route('/home')
def home():
    return "HOME"


if __name__ == '__main__':
    app.run(debug=True)
