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

# -------------------------------------  {{{ read config

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


class Test(object):  # need database connection

    def setUp(self):
        create_tables()
        Database.config(db=mysql_db, user=mysql_user, passwd=mysql_passwd)

    def tearDown(self):
        drop_tables()
        Database.query_times = 0
        Database.SQL = None

    def create_data(self, count, table=None):
        if table is 1:  # only create data in user
            for i in range(1, count+1):
                User.create(name="name"+str(i), email="email"+str(i))
        elif table is 2:  # only create data in post
            for i in range(1, count+1):
                Post.create(name="name"+str(i), user_id=count+1-i)
        else:  # in both, default
            for i in range(1, count+1):
                User.create(name="name"+str(i), email="email"+str(i))
            for i in range(1, count+1):
                Post.create(name="name"+str(i), user_id=count+1-i)


class TestDatabase_:

    def test_config(self):
        Database.config(db=mysql_db, user=mysql_user, passwd=mysql_passwd,
                        charset="utf8", autocommit=True)


class TestDatabase(Test):

    def test_connect(self):
        Database.connect()

    def test_get_conn(self):
        c1 = Database.connect()
        c2 = Database.connect()
        assert c1 is c2

    def test_execute(self):
        Database.execute("insert into user set name='hello'")


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


class TestExpr:

    def test_op(self):
        expr1 = User.name == "Join"
        expr2 = User.email == "Join@github.com"
        assert expr1 & expr2 == "user.name = 'Join' and user.email = 'Join@github.com'"
        assert expr1 | expr2 == "user.name = 'Join' or user.email = 'Join@github.com'"


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
        assert User.at(1).update(User.name == "newname") == 1L
        assert User.at(2).update(email="newemail") == 1L

    def test_select(self):
        self.create_data(4, table=1)
        user = User.at(1).select().fetchone()
        assert user._id == 1L
        for user in User.select(User.name).fetchall():
            assert user._id and user.name

    def test_delete(self):
        self.create_data(4, table=1)
        assert User.at(1).delete() == 1L
        assert User.where(
            (User.name == "name2") | (User.name == "name3")
        ).delete() == 2L

    def test_where(self):
        self.create_data(3, table=1)
        assert User.where(User.id == 1) is User
        assert User.where(id=1) is User
        assert User.where(User.name == "name1").select().count == 1L
        assert User.where(
            User.name == "name1", User.email == "email"
        ).select().count == 0L
        assert User.where(
            User.name == "name1", email="email"
        ).select().count == 0L
        assert User.where(name="name1", email="email1").select().count == 1L

    def test_at(self):
        self.create_data(3, table=1)
        assert User.at(1).select().count == 1L
        assert User.at(-1).select().count == 0
        assert User.at(1).select().fetchone().name == "name1"
        assert User.at(1).delete()

    def test_orderby(self):
        self.create_data(3, table=1)
        users = User.orderby(User.id, desc=True).select(User.name).fetchall()
        user1, user2, user3 = tuple(users)
        assert user1.id > user2.id > user3.id

    def test_modelobj_save(self):
        user = User(name="jack", email="jack@github.com")
        assert user.save()
        assert User.select().count == 1L
        user.name = "li"
        assert user.save()
        assert User.at(1).select().fetchone().name == "li"

    def test_modelobj_destroy(self):
        self.create_data(3, table=1)
        user = User.at(1).select().fetchone()
        assert user.destroy()
        assert User.at(1).select().fetchone() is None


class TestModels_:

    def setUp(self):
        sys.path.insert(0, "..")
        from CURD import Models
        self.models = Models(User, Post)

    def test_table_name(self):
        assert self.models.table_name == "user, post"

    def test_primarykey(self):
        assert self.models.primarykey == [User.id, Post.post_id]


class TestModels(Test):

    def setUp(self):
        sys.path.insert(0, "..")
        from CURD import Models
        super(TestModels, self).setUp()
        self.create_data(4)
        self.models = Models(Post, User)

    def test_where(self):
        assert self.models.where(User.id == Post.user_id).select().count == 4L
        assert self.models.where(
            User.id == Post.user_id, User.id == 1
        ).select().count == 1L

    def test_select(self):
        for post, user in self.models.where(
            User.id == Post.user_id
        ).select().fetchall():
            assert user.id == post.user_id

        post, user = self.models.where(
            Post.post_id == User.id
        ).select().fetchone()

        assert user.id == post.post_id

    def test_update(self):
        assert self.models.where(
            User.id == Post.user_id
        ).update(User.name == "new") == 4L

    def test_delete(self):
        assert self.models.where(User.id == Post.user_id).delete() == 8L
        assert self.models.where(User.id == Post.user_id).select().count == 0L

    def test_delete2(self):
        assert self.models.where(User.id == Post.user_id).delete(Post) == 4L
        assert User.select().count == 4L
        assert Post.select().count == 0L

    def test_orderby(self):
        G = self.models.where(
            Post.post_id == User.id
        ).orderby(User.name, 1).select().fetchall()
        d = tuple(G)
        assert d == tuple(sorted(d, key=lambda x: x[1].name, reverse=True))



class TestJoinModel(Test):

    def setUp(self):
        super(TestJoinModel, self).setUp()
        self.create_data(10)

    def test_select(self):
        assert (Post & User).select().count == 10L
        assert (Post & User).where(User.name == "name2").select().count == 1L
        for post, user in (Post & User).select().fetchall():
            assert post.post_id
            assert user.id
            assert post.user_id == user.id

    def test_delete(self):
        assert (Post & User).delete() == 20L
        assert (Post & User).select().count == 0L

    def test_delete2(self):
        assert (Post & User).delete(Post) == 10L

    def test_update(self):
        assert (Post & User).where(
            User.name <= "name4"
        ).update(User.name == "hello") == 5L
        assert (Post & User).where(
            User.name == "hello"
        ).update(Post.name == "good") == 5L


# select_result Tests

class TestSelect_result(Test):

    def test_count(self):
        self.create_data(5)
        assert User.select().count == 5L

    def test_fetchone(self):
        self.create_data(4)
        user = User.at(1).select().fetchone()
        assert user.id == 1L

    def test_fetchall(self):
        self.create_data(4)
        for user in User.select().fetchall():
            assert user._id


class TestSugar(Test):

    def setUp(self):
        super(TestSugar, self).setUp()
        sys.path.insert(0, '..')
        from CURD import Sugar

    def test_Model_getitem(self):
        self.create_data(4)
        user1 = User[1]
        user2 = User[2]
        assert user1.name == "name1"
        assert user2.name == "name2"

    def test_Model_getslice(self):
        self.create_data(4)
        users = User[1:3]
        for user in users:
            assert user.id

    def test_in(self):  # in operator
        user = User.create(name="myname", email="myemail")
        assert user in User
        user1 = User(User.name == "myname")
        assert user1 in User
        user1.email = "email"
        assert user1 not in User
