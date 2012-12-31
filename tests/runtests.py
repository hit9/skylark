#
# run tests with nose: nosetests runtests.py
# This tests are based on the API list in doc/API.md
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


#create tables & droptables using MySQLdb

import MySQLdb

conn = MySQLdb.connect(db=mysql_db, user=mysql_user, passwd=mysql_passwd)

create_tbl_SQL = open("tables.sql").read()


def create_tables():
    conn.cursor().execute(create_tbl_SQL)


def drop_tables():
    conn.cursor().execute("drop table user, post")


# Tests begin

from models import *    # import models from models.py


class Test:  # need database connection

    def setUp(self):
        create_tables()
        Database.config(db=mysql_db, user=mysql_user, passwd=mysql_passwd)

    def tearDown(self):
        drop_tables()
        Database.query_times = 0
        Database.SQL = None


# Database Tests

class TestDatabase_:

    def test_config(self):
        Database.config(db=mysql_db, user=mysql_user, passwd=mysql_passwd)


class TestDatabase(Test):

    def test_execute(self):
        SQL = "insert user set name = 'hello'"
        cursor = Database.execute(SQL)
        return SQL

    def test_SQL(self):
        SQL = self.test_execute()
        assert Database.SQL == SQL

    def test_query_times(self):
        assert Database.query_times is 0
        self.test_execute()
        print Database.query_times
        assert Database.query_times is 1


# Model, modelObj Tests

class TestMoel_:

    def test_data(self):
        user1 = User(name="name1")
        user2 = User(User.name == "name2", email="email2")
        assert user1._data == {"name": "name1"}
        assert user2._data == {"name": "name2", "email": "email2"}

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


class TestModel(Test):

    def create_data(self, count=1):
        for i in range(count):
            User.create(name="name"+str(i), email="email"+str(i))

    def test_create(self):
        user1 = User.create(name="name1", email="email1")
        user2 = User.create(User.name == "name2", email="email2")
        user3 = User.create(User.name == "name3", email="email3")
        assert user1._id and user2._id and user3._id

    def test_update(self):
        self.create_data(2)
        assert User.at(1).update(User.name == "newname") is 1
        assert User.at(2).update(email="newemail") is 1

    def test_select(self):
        self.create_data(4)
        user = User.at(1).select().fetchone()
        assert user._id == 1L
        for user in User.select(User.name).fetchall():
            assert user._id and user.name

    def test_delete(self):
        self.create_data(4)
        assert User.at(1).delete() is 1
        assert User.where(
            (User.name == "name2") | (User.name == "name3")
        ).delete() is 2

    def test_where(self):
        self.create_data(3)
        assert User.where(User.id == 1) is User
        assert User.where(id=1) is User
        assert User.where(User.name == "name1").select().count is 1
