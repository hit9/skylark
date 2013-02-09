#
# run tests with nose:
#
# $ nosetests
#
#
# Test Case Class Names:
#   Testxxx(Test)  => Need Database Connection
#   Testxxx_       => Do Not Need Database Connection
#

import sys

# read config

import ConfigParser

cf = ConfigParser.ConfigParser()
cf.read("mysql.conf")

mysql_user = cf.get("MySQL", "user")
mysql_passwd = cf.get("MySQL", "passwd")
mysql_db = cf.get("MySQL", "db")


# create tables & droptables using MySQLdb

import MySQLdb

conn = MySQLdb.connect(db=mysql_db, user=mysql_user, passwd=mysql_passwd)

create_tbl_SQL = open("tables.sql").read()


def create_tables():
    conn.cursor().execute(create_tbl_SQL)


def drop_tables():
    conn.cursor().execute("drop table post, user")

from models import *


class Test(object):  # need database connection

    def setUp(self):
        create_tables()
        Database.config(db=mysql_db, user=mysql_user, passwd=mysql_passwd)

    def tearDown(self):
        drop_tables()
        Database.query_times = 0
        Database.SQL = None


class TestDatabase_:

    def test_config(self):
        Database.config(db=mysql_db, user=mysql_user, passwd=mysql_passwd,
                        charset="utf8", autocommit=True, debug=True)


class TestDatabase(Test):

    def test_connect(self):
        Database.connect()
        Database.connect()

    def test_get_conn(self):
        c1 = Database.connect()
        c2 = Database.connect()
        assert c1 is c2

    def test_execute(self):
        Database.execute("insert into user set name='hello'")

    def test_SQL(self):
        SQL = "insert into user set name = 'hello'"
        Database.execute(SQL)
        assert Database.SQL == SQL

    def test_query_times(self):
        SQL = "insert into user set name = 'hello'"
        assert Database.query_times is 0
        Database.execute(SQL)
        print Database.query_times
        assert Database.query_times is 1


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

    def test_operator(self):

        sys.path.append('..')

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
        assert tostr(expr1) == "user.id < '4'"
        assert tostr(expr2) == "user.id <= '4'"
        assert tostr(expr3) == "user.id > '4'"
        assert tostr(expr4) == "user.id >= '4'"
        assert tostr(expr5) == "user.id <> '4'"
        assert tostr(expr6) == "user.id = '4'"
        assert tostr(expr7) == "user.id + '4'"
        assert tostr(expr8) == "user.id between 3 and 4"
        assert tostr(expr9) == "user.id in (1, 2, 3)"
