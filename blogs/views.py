from flask import Flask, Blueprint, request, abort, redirect, session, jsonify, render_template
from config import mydb
from auth.views import login_required
from utils.db_help import get_user_by_email

blogs = Blueprint('blogs', __name__)


@blogs.route("/home-page")
@login_required
def home_page():
    return "homepage"


@blogs.route("/personal-page")
def home_page():
    return "personalpage"


@blogs.route("/blog", methods=["GET"])
def get_blog():
    return render_template('blog_form.html')


@blogs.route("/blog", methods=["POST"])
def post_blog():
    result = request.form.to_dict()
    user_id = get_user_by_email(session["email"])
    print(user_id)
    sql = '''
        INSERT INTO blog(blog_title, blog_description, user_id) values ('{0}','{1}',{2})
    '''.format(result.get('blog_title'), result.get('blog_description'), user_id)
    mysql = mydb.cursor()
    mysql.execute(sql)
    mydb.commit()
    mysql.close()
    return jsonify(result)
