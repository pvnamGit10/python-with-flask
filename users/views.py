import json

from flask import Flask, Blueprint, request, abort, redirect, session, jsonify, render_template
from config import mydb

users = Blueprint('users', __name__)


@users.route('/input-info-require', methods=["POST"])
def input_field_require():
    if not request.json or not 'user_name' and 'user_phone' in request.json:
        abort(400, "You must fill all information")
    sql = '''
        UPDATE user_google set user_name = '{0}', user_phone = '{1}' where user_email = '{2}'
    '''.format(request.json['user_name'], request.json['user_phone'], session["email"])
    mysql = mydb.cursor()
    mysql.execute(sql)
    mydb.commit()
    mysql.close()
    return redirect("/home")


@users.route('/input-info', methods=["GET"])
def input_info_get():
    return render_template('information_form.html')


@users.route("/input-info", methods=["POST"])
def input_info_post():
    result = request.form.to_dict()
    # sql = '''
    #             UPDATE user_google set user_name = '{0}', phone = '{1}' where email = '{2}'
    #         '''.format(result.get('user_name'), result.get('user_phone'), session["email"])
    # mysql = mydb.cursor()
    # mysql.execute(sql)
    # mydb.commit()
    # mysql.close()
    return jsonify({'form': result})
