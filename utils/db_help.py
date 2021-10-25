import itertools

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


def get_blog_like(blog_id):
    sql = '''
        select u.user_name
        from user_google u
        join blog_like bl on u.id = bl.user_id
        join blog b on b.id = bl.blog_id
        where b.id = {0}
    '''.format(blog_id)
    mysql = mydb.cursor()
    mysql.execute(sql)
    data = mysql.fetchall()
    list_data = list(itertools.chain.from_iterable(data))
    mysql.close()
    return list_data


def check_like_status(user_id, blog_id):
    sql = '''
        select u.id
        from user_google u
        join blog_like bl on u.id = bl.user_id
        join blog b on b.id = bl.blog_id
        where b.id = {0} and u.id= {1}
    '''.format(blog_id,user_id)
    mysql = mydb.cursor()
    mysql.execute(sql)
    user = mysql.fetchone()
    mysql.close()
    if(type(user) == tuple):
        return True
    else:
        return False


def like_blog(user_id, blog_id):
    sql = '''
        Insert into blog_like(user_id, blog_id) values ({0},{1})
    '''.format(user_id, blog_id)
    mysql = mydb.cursor()
    mysql.execute(sql)
    mydb.commit()
    mysql.close()
