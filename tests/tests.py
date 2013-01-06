#
# run tests with nose:
#
# $ nosetests
#
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


class Test(object):  # need database connection

    def setUp(self):
        create_tables()
        Database.config(db=mysql_db, user=mysql_user, passwd=mysql_passwd)

    def tearDown(self):
        drop_tables()
        Database.query_times = 0
        Database.SQL = None

    def create_data(self, count=1):
        for i in range(1, count+1):
            User.create(name="name"+str(i), email="email"+str(i))
            Post.create(name="name"+str(i), user_id=count+1-i)


# Database Tests

class TestDatabase_:

    def test_config(self):
        Database.config(db=mysql_db, user=mysql_user, passwd=mysql_passwd)


class TestDatabase(Test):

    def test_execute(self):
        SQL = "insert into user set name = 'hello'"
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


# Field Tests

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
        expr1 = User.id < 4
        expr2 = User.id <= 4
        expr3 = User.id > 4
        expr4 = User.id >= 4
        expr5 = User.id != 4
        expr6 = User.id == 4
        expr7 = User.id + 4
        assert expr1._tostr == "user.id < '4'"
        assert expr2._tostr == "user.id <= '4'"
        assert expr3._tostr == "user.id > '4'"
        assert expr4._tostr == "user.id >= '4'"
        assert expr5._tostr == "user.id <> '4'"
        assert expr6._tostr == "user.id = '4'"
        assert expr7._tostr == "user.id + '4'"


# Expr Tests

class TestExpr_:

    def test_op(self):
        expr = User.name == "myname"
        assert expr.op == " = "

    def test_tostr(self):
        expr = User.name == "myname"
        expr1 = (User.id >= 10) & (User.name == "name")
        assert expr._tostr == "user.name = 'myname'"
        assert expr1._tostr == "user.id >= '10' and user.name = 'name'"

    def test_operator(self):
        expr1 = (User.name == "name") & (User.email == "email")
        expr2 = (User.name == "name") | (User.email == "email")
        assert expr1._tostr == "user.name = 'name' and user.email = 'email'"
        assert expr2._tostr == "user.name = 'name' or user.email = 'email'"


# Model, modelObj Tests

class TestModel_:

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

    def test_operator(self):
        A = Post & User
        assert isinstance(A, JoinModel)
        assert A.models == [Post, User]


class TestModel(Test):

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
        assert User.where(
            User.name == "name1", User.email == "email"
        ).select().count is 0
        assert User.where(
            User.name == "name1", email="email"
        ).select().count is 0
        assert User.where(name="name1", email="email1").select().count is 1

    def test_at(self):
        self.create_data(3)
        assert User.at(1).select().count is 1
        assert User.at(-1).select().count is 0
        assert User.at(1).select().fetchone().name == "name1"
        assert User.at(1).delete()

    def test_orderby(self):
        self.create_data(3)
        users = User.orderby(User.id, desc=True).select(User.name).fetchall()
        user1, user2, user3 = tuple(users)
        assert user1.id > user2.id > user3.id

    def test_modelobj_save(self):
        user = User(name="jack", email="jack@github.com")
        assert user.save()
        assert User.select().count is 1
        user.name = "li"
        assert user.save()
        assert User.at(1).select().fetchone().name == "li"

    def test_modelobj_destroy(self):
        self.create_data(3)
        user = User.at(1).select().fetchone()
        assert user.destroy()
        assert User.at(1).select().fetchone() is None

    def test_in(self):  # in operator
        user = User.create(name="myname", email="myemail")
        assert user in User
        user1 = User(User.name == "myname")
        assert user1 in User
        user1.email = "email"
        assert user1 not in User


# Models Tests

class TestModels_:

    def setUp(self):
        self.models = Models(User, Post)

    def test_table_name(self):
        assert self.models.table_name == "user, post"

    def test_primarykey(self):
        assert self.models.primarykey == [User.id, Post.post_id]


class TestModels(Test):

    def setUp(self):
        super(TestModels, self).setUp()
        self.create_data(4)
        self.models = Models(User, Post)

    def test_where(self):
        assert self.models.where(User.id == Post.user_id).select().count is 4
        assert self.models.where(
            User.id == Post.user_id, User.id == 1
        ).select().count is 1

    def test_select(self):
        for user, post in self.models.where(
            User.id == Post.user_id
        ).select().fetchall():
            assert user.id == post.user_id

        user, post = self.models.where(
            Post.post_id == User.id
        ).select().fetchone()

        assert user.id == post.post_id

    def test_update(self):
        assert self.models.where(
            User.id == Post.user_id
        ).update(User.name == "new") is 4

    def test_delete(self):
        assert self.models.where(User.id == Post.user_id).delete() is 8
        assert self.models.where(User.id == Post.user_id).select().count is 0

    def test_delete2(self):
        assert self.models.where(User.id == Post.user_id).delete(User) is 4
        assert User.select().count is 0
        assert Post.select().count is 4

    def test_orderby(self):
        G = self.models.where(
            Post.post_id == User.id
        ).orderby(User.name, 1).select().fetchall()
        d = tuple(G)
        assert d == tuple(sorted(d, key=lambda x: x[0].name, reverse=True))


class TestJoinModel_:

    def test_bridge(self):
        assert (Post & User).bridge is Post.user_id


class TestJoinModel(Test):

    def setUp(self):
        super(TestJoinModel, self).setUp()
        self.create_data(10)

    def test_select(self):
        assert (Post & User).select().count is 10
        assert (Post & User).where(User.name == "name2").select().count is 1
        for post, user in (Post & User).select().fetchall():
            assert post.post_id
            assert user.id
            assert post.user_id == user.id

    def test_delete(self):
        assert (Post & User).delete() is 20
        assert (Post & User).select().count is 0

    def test_delete2(self):
        assert (Post & User).delete(Post) is 10

    def test_update(self):
        assert (Post & User).where(
            User.name <= "name4"
        ).update(User.name == "hello") is 5
        assert (Post & User).where(
            User.name == "hello"
        ).update(Post.name == "good") is 5


# select_result Tests

class Testselect_result(Test):

    def test_count(self):
        self.create_data(5)
        assert User.select().count is 5

    def test_fetchone(self):
        self.create_data(4)
        user = User.at(1).select().fetchone()
        assert user.id == 1

    def test_fetchall(self):
        self.create_data(4)
        for user in User.select().fetchall():
            assert user._id
