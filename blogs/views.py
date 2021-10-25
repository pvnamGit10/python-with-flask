import json
from flask import Flask, Blueprint, request, abort, redirect, session, jsonify, render_template


from config import mydb
from auth.views import login_required
from utils.db_help import get_user_by_email, get_blog_like, check_like_status, like_blog

blogs = Blueprint('blogs', __name__)


@blogs.route("/personal-page")
def personal_page():
    return "personalpage"


@blogs.route("/home-page")
def home_page():
    sql = '''
        select id, blog_title, blog_description from blog
    '''
    mysql = mydb.cursor()
    mysql.execute(sql)
    blog_list = list(mysql.fetchall())
    i = 0
    for index in blog_list:
        blog = list(index)
        likes = get_blog_like(index[0])
        if (len(likes) <= 2 and len(likes) > 0):
            blog.append(' '.join([str(ele) for ele in likes]) + " liked this")
        elif (len(likes) > 2):
            blog.append(
                str(likes[0]) + ", " + str(likes[1]) + " and " + str((len(likes) - 2)) + " others people liked this")
        if (check_like_status(get_user_by_email(session["email"]), blog[0])):
            blog.append("LIKED")
        else:
            blog.append(('<a href=/blog/'+str(blog[0])+'?action=like/>'))
        blog_list[i] = blog
        i = i + 1
    return jsonify({'blog_list': blog_list, 'status': True})


@blogs.route("/blog", methods=["GET"])
def get_blog():
    return render_template('blog_form.html')


@blogs.route("/blog", methods=["POST"])
def post_blog():
    result = request.form.to_dict()
    user_id = get_user_by_email(session["email"])
    sql = '''
        INSERT INTO blog(blog_title, blog_description, user_id) values ('{0}','{1}',{2})
    '''.format(result.get('blog_title'), result.get('blog_description'), user_id)
    mysql = mydb.cursor()
    mysql.execute(sql)
    mydb.commit()
    mysql.close()
    return redirect("/home-page")


@blogs.route("/blog/<blog_id>")
def blog_details(blog_id):
    if (request.args.get("action") == "like"):
        user_id = get_user_by_email(session["email"])
        like_blog(int(user_id), int(blog_id))
        return redirect("/home-page")
    sql = '''
        select id, blog_title, blog_description from blog where id = {0}
    '''.format(blog_id)
    mysql = mydb.cursor()
    mysql.execute(sql)
    blog = mysql.fetchone()
    mysql.close()
    return jsonify({'data': blog})

