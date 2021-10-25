import functools
import os.path
import pathlib

import flask
import requests_oauthlib

from utils.db_help import user_already_existed
from google.auth.transport import requests
import google.auth.transport.requests
from flask import session, abort, redirect, request, jsonify, Blueprint

from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from pip._vendor import cachecontrol
from config import mydb
from requests_oauthlib.compliance_fixes import facebook_compliance_fix

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

URL = "http://127.0.0.1:5000/"


def login_required(function):
    @functools.wraps(function)
    def wrapper(*args, **kwargs):
        if "google_id" not in session:
            return abort(401)  # Authorization required
        else:
            return function()

    return wrapper


@auth.route("/register-by-google")
def register_google():
    authorization_url, state = flow.authorization_url()
    session["state"] = state
    session["status"] = "register"
    return redirect(authorization_url)


@auth.route("/login-by-google")
def login_by_google():
    authorization_url, state = flow.authorization_url()
    session["state"] = state
    session["status"] = "login"
    return redirect(authorization_url)


@auth.route("/fb-login")
def login_by_fb():
    return "fb"


@auth.route("/callback")
def callback():
    # Use the authorization server's response to fetch the OAuth 2.0 tokens
    flow.fetch_token(authorization_response=request.url)

    # Specify the state when creating the flow in the callback so that it can
    # verified in the authorization server response.
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
    if session["status"] == "login":
        if not user_already_existed(session["email"]):
            return jsonify(400, {'message': "Must register", 'status': False})
        else:
            return redirect("/home-page")

    if session["status"] == "register":
        if user_already_existed(session["email"]):
            return redirect("/login-by-google")

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
    return redirect("/input-info")


@auth.route("/logout")
def logout():
    session.clear()
    return redirect("/")
