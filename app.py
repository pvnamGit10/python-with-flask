from flask import Flask, session
from auth.views import auth
from users.views import users
from blogs.views import blogs

app = Flask(__name__)

app.secret_key = "SECRETE TEST"

app.register_blueprint(auth)
app.register_blueprint(users)
app.register_blueprint(blogs)


@app.route('/')
def hello_world():
    print(session)
    return 'hoho'


@app.route('/home')
def home():
    return "HeE"


if __name__ == '__main__':
    app.run(debug=True)
