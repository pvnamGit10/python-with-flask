import os.path
import pathlib

from google.auth.transport import requests
import google.auth.transport.requests
from flask import session, abort, redirect, request, jsonify, Blueprint

from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from pip._vendor import cachecontrol
from pyasn1.debug import Debug
from config import mydb

auth = Blueprint('auth', __name__)

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

GOOGLE_CLIENT_ID = "717951336721-hgkj374d6nkuf3b10hp9f00iqln5tffk.apps.googleusercontent.com"
client_secrets_file = os.path.join(pathlib.Path(__file__).parent, "client_secrete_api.json")

flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email",
            "openid"],
    redirect_uri="http://127.0.0.1:5000/callback"
)


def login_required(function):
    def wrapper(*args, **kwargs):
        if "google_id" not in session:
            return abort(401)  # Authorization required
        else:
            return function()

    return wrapper


def user_already_existed(email):
    sql = '''
        SELECT id from user_google where email = '{0}'
    '''.format(email)
    mysql = mydb.cursor()
    mysql.execute(sql)
    data = mysql.fetchall()
    mysql.close()
    return bool(len(data) > 0)


@auth.route("/register-by-google")
def login():
    authorization_url, state = flow.authorization_url()
    session["state"] = state
    return redirect(authorization_url)


@auth.route("/callback")
def callback():
    flow.fetch_token(authorization_response=request.url)

    if not session["state"] == request.args["state"]:
        abort(500)  # State does not match!

    credentials = flow.credentials
    request_session = requests.AuthorizedSession(credentials)
    cached_session = cachecontrol.CacheControl(request_session)
    token_request = google.auth.transport.requests.Request(session=cached_session)

    id_info = id_token.verify_oauth2_token(
        id_token=credentials._id_token,
        request=token_request,
        audience=GOOGLE_CLIENT_ID
    )

    session["google_id"] = id_info.get("sub")
    session["name"] = id_info.get("name")
    session["email"] = id_info.get("email")

    return redirect("/register-info")


@auth.route('/register-info')
def register_info():
    if user_already_existed(session["email"]):
        return redirect("/")
    sql = '''
        INSERT INTO user_google(email) values ('{0}')
    '''.format(session["email"])
    mysql = mydb.cursor()
    mysql.execute(sql)
    mydb.commit()
    mysql.close()
    return redirect("/home")

@auth.route("/logout")
def logout():
    session.clear()
    return redirect("/")
