from config import mydb


def user_already_existed(email):
    sql = '''
        SELECT id from user_google where email = '{0}'
    '''.format(email)
    mysql = mydb.cursor()
    mysql.execute(sql)
    data = mysql.fetchall()
    mysql.close()
    return bool(len(data) > 0)


def get_user_by_email(email):
    sql = '''
            SELECT distinct id from user_google where email = '{0}' limit 1
        '''.format(email)
    mysql = mydb.cursor()
    mysql.execute(sql)
    data = mysql.fetchone()
    mysql.close()
    return data[0]
