# coding=utf8
#
# run tests with nose:
#
#    $ nosetests
#
# Test Case Class Names:
# Testxxx(Test) => Need Database Connection
# Testxxx_ => Do Not Need Database Connection


import sys
import ConfigParser


# ------------------------------------- {{{ read config

import ConfigParser

cf = ConfigParser.ConfigParser()
cf.read("mysql.conf")

mysql_user = cf.get("MySQL", "user")
mysql_passwd = cf.get("MySQL", "passwd")
mysql_db = cf.get("MySQL", "db")

# --------------------------------------- read config }}}


# create tables & droptables using MySQLdb

import MySQLdb

conn = MySQLdb.connect(db=mysql_db, user=mysql_user, passwd=mysql_passwd)

create_tbl_SQL = open("tables.sql").read()


def create_tables():
    conn.cursor().execute(create_tbl_SQL)


def drop_tables():
    conn.cursor().execute("drop table post, user")


from models import *

sys.path.insert(0, '..')
from CURD import Compiler


class Test(object):  # classes inhrite from Test need database connection

    def setUp(self):
        create_tables()
        Database.config(db=mysql_db, user=mysql_user, passwd=mysql_passwd)

    def tearDown(self):
        drop_tables()

    def create_data(self, count, table=None):
        if table is 1:  # only create data in user
            for i in range(1, count+1):
                User.create(name="name"+str(i), email="email"+str(i))
        elif table is 2:  # only create data in post
            for i in range(1, count+1):
                Post.create(name="name"+str(i), user_id=count+1-i)
        else: # in both, default
            for i in range(1, count+1):
                User.create(name="name"+str(i), email="email"+str(i))
            for i in range(1, count+1):
                Post.create(name="name"+str(i), user_id=count+1-i)


class TestDatabase_:

    def test_config(self):
        Database.config(db=mysql_db, user=mysql_user, passwd=mysql_passwd,
                        charset='utf8', autocommit=True)


class TestDatabase(Test):

    def test_connect(self):
        Database.connect()

    def test_get_conn(self):
        conn1 = Database.get_conn()
        conn2 = Database.get_conn()
        assert conn1 is conn2

    def test_execute(self):
        Database.execute('insert into user set user.name="test"')


class TestField_:

    def test_name(self):
        assert User.name.name == "name"
        assert User.email.name == "email"
        assert Post.name.name == "name"
        assert Post.user_id.name == "user_id"

    def test_fullname(self):
        assert User.name.fullname == "user.name"
        assert User.email.fullname == "user.email"
        assert Post.name.fullname == "post.name"
        assert Post.user_id.fullname == "post.user_id"

    def test_primarykey(self):
        assert User.name.is_primarykey is False
        assert User.id.is_primarykey is True
        assert Post.post_id.is_primarykey is True

    def test_foreignkey(self):
        assert User.name.is_foreignkey is False
        assert User.email.is_foreignkey is False
        assert Post.user_id.is_foreignkey is True
        assert Post.user_id.point_to is User.id


class TestExpr_:

    def test_op(self):
        expr1 = User.name == "Join"
        expr2 = User.email == "Join@github.com"
        assert expr1 & expr2 == "user.name = 'Join' and user.email = 'Join@github.com'"
        assert expr1 | expr2 == "user.name = 'Join' or user.email = 'Join@github.com'"

    def test_operator(self):

        sys.path.insert(0, '..')

        from CURD import Compiler

        tostr = Compiler.parse_expr

        expr1 = User.id < 4
        expr2 = User.id <= 4
        expr3 = User.id > 4
        expr4 = User.id >= 4
        expr5 = User.id != 4
        expr6 = User.id == 4
        expr7 = User.id + 4
        expr8 = User.id.between(3, 4)
        expr9 = User.id._in(1, 2, 3)
        expr10 = User.name.like("%Join%")
        expr11 = User.id.not_in(1, 2, 3)
        assert tostr(expr1) == "user.id < 4"
        assert tostr(expr2) == "user.id <= 4"
        assert tostr(expr3) == "user.id > 4"
        assert tostr(expr4) == "user.id >= 4"
        assert tostr(expr5) == "user.id <> 4"
        assert tostr(expr6) == "user.id = 4"
        assert tostr(expr7) == "user.id + 4"
        assert tostr(expr8) == "user.id between 3 and 4"
        assert tostr(expr9) == "user.id in (1, 2, 3)"
        assert tostr(expr10) == "user.name like '%Join%'"
        assert tostr(expr11) == "user.id not in (1, 2, 3)"

    def test_parser_cache(self):

        tostr = Compiler.parse_expr

        expr1 = User.id == 199
        expr2 = User.id == 199
        assert expr1 is not expr2
        assert expr1 == expr2
        assert tostr(expr1) is tostr(expr2)

    def test_unicode(self):

        tostr = Compiler.parse_expr

        expr = User.name == u"你好世界"

        assert tostr(expr) == "user.name = '你好世界'"


class TestModel_:

    def test_data(self):
        user1 = User(name="Mark")
        user2 = User(User.email == "Mark@gmail.com")
        assert user1.data == {"name": "Mark"}
        assert user2.data == {"email": "Mark@gmail.com"}

    def test_modelobj_fieldname(self):
        user = User(name="name1")
        assert user.name == "name1"

    def test_model_fieldname(self):
        assert isinstance(User.name, Field)
        assert isinstance(User.email, Field)

    def test_table_name(self):
        assert User.table_name == "user"
        assert Post.table_name == "post"

    def test_primarykey(self):
        user_id = User.primarykey
        post_id = Post.primarykey
        assert user_id.name == "id"
        assert post_id.name == "post_id"

    def test_operator(self):
        A = Post & User
        assert A.models == [Post, User]
        assert A.primarykey == [Post.post_id, User.id]


class TestModel(Test):

    def test_create(self):
        user1 = User.create(name="name1", email="email1")
        user2 = User.create(User.name == "name2", email="email2")
        user3 = User.create(User.name == "name3", email="email3")
        assert user1._id and user2._id and user3._id

    def test_update(self):
        self.create_data(2, table=1)
        assert User.at(1).update(User.name == "newname").execute() == 1L
        assert User.at(2).update(email="newemail").execute() == 1L

    def test_select(self):
        self.create_data(4, table=1)
        query = User.at(1).select()
        result = query.execute()
        assert result.count == 1L
        user = result.fetchone()
        assert user._id == 1L
        for user in User.select(User.name):
            assert user._id and user.name

    def test_delete(self):
        self.create_data(4, table=1)
        assert User.at(1).delete().execute() == 1L
        assert User.where(
            (User.name == "name2") | (User.name == "name3")
        ).delete().execute() == 2L

    def test_where(self):
        self.create_data(3, table=1)
        assert User.where(User.id == 1) is User
        assert User.where(id=1) is User
        User.runtime.reset_data()
        assert User.where(User.name == "name1").select().execute().count == 1L
        assert User.where(
            User.name == "name1", User.email == "email"
        ).select().execute().count == 0L
        assert User.where(
            User.name == "name1", email="email"
        ).select().execute().count == 0L
        assert User.where(name="name1", email="email1").select().execute().count == 1L

    def test_at(self):
        self.create_data(3, table=1)
        assert User.at(1).select().execute().count == 1L
        assert User.at(-1).select().execute().count == 0
        assert User.at(1).select().execute().fetchone().name == "name1"
        assert User.at(1).delete().execute()

    def test_orderby(self):
        self.create_data(3, table=1)
        users = User.orderby(User.id, desc=True).select(User.name).execute().fetchall()
        user1, user2, user3 = tuple(users)
        assert user1.id > user2.id > user3.id

    def test_modelobj_save(self):
        user = User(name="jack", email="jack@github.com")
        assert user.save()
        assert User.select().execute().count == 1L
        user.name = "li"
        assert user.save()
        assert User.at(1).select().execute().fetchone().name == "li"

    def test_modelobj_destroy(self):
        self.create_data(3, table=1)
        user = User.at(1).select().execute().fetchone()
        assert user.destroy()
        assert User.at(1).select().execute().fetchone() is None

    def test_select_without_primaryeky(self):
        self.create_data(3, table=1)
        user = User.at(1).select_without_primarykey(User.name).execute().fetchone()
        try:
            name = user.name
        except KeyError:
            pass

    def test_findone(self):
        self.create_data(3, table=1)
        user = User.findone(name="name1")
        assert User.id

    def test_findall(self):
        self.create_data(3, table=1)
        users = User.findall(User.name.like("name%"))
        assert len(list(users)) is 3

    def test_getone(self):
        self.create_data(3, table=1)
        user = User.at(1).getone()
        assert user.id == 1L

    def test_getall(self):
        self.create_data(3, table=1)
        users = User.where(User.name=="name1").getall()
        assert len(list(users)) is 1

