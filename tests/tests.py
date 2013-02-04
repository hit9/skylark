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
