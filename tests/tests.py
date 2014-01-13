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
from CURD import *


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

    def test_change(self):
        """Database.change needn't change connection object!"""
        c = Database.conn
        Database.change(mysql_db)
        assert Database.conn is c


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


class TestFunction_:

    def test_name(self):
        assert Fn.count(User.id).name == 'count_of_id'
        assert Fn.count(Post.post_id).name == 'count_of_post_id'

    def test_fullname(self):
        assert Fn.max(User.id).fullname == 'max(user.id)'
        assert Fn.count(User.id).fullname == 'count(user.id)'
        assert Fn.count(Post.post_id).fullname == 'count(post.post_id)'

    def test_model(self):
        assert Fn.min(User.id).model is User
        assert Fn.lcase(Post.name).model is Post



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
        assert tostr(expr1) == "user.id < '4'"
        assert tostr(expr2) == "user.id <= '4'"
        assert tostr(expr3) == "user.id > '4'"
        assert tostr(expr4) == "user.id >= '4'"
        assert tostr(expr5) == "user.id <> '4'"
        assert tostr(expr6) == "user.id = '4'"
        assert tostr(expr7) == "user.id + '4'"
        assert tostr(expr8) == "user.id between '3' and '4'"
        assert tostr(expr9) == "user.id in ('1', '2', '3')"
        assert tostr(expr10) == "user.name like '%Join%'"
        assert tostr(expr11) == "user.id not in ('1', '2', '3')"

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
        assert ATableDoseNotExist.table_name == 'a_table_dose_not_exist'
        assert TableDoseNotExist.table_name == 'a_table_name'

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
            assert user.name

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
        users = User.orderby(User.id, desc=True).select(User.id, User.name).execute().fetchall()
        user1, user2, user3 = tuple(users)
        assert user1.id > user2.id > user3.id

    def test_groupby(self):

        for x in range(2):
            User.create(name='jack', email='jack@github.com')

        for x in range(3):
            User.create(name='tom', email='jack@github.com')

        query = User.groupby(User.name).select(Fn.count(User.id), User.name)

        for user in query:
            if user.name == 'jack':
                assert user.count_of_id == 2L
            elif user.name == 'tom':
                assert user.count_of_id == 3L

        query = User.groupby(User.email).select(Fn.count(User.id))
        result = query.execute()
        assert result.count == 1L
        assert result.fetchone().count_of_id == 5L

    def test_having(self):
        for x in range(2):
            User.create(name='jack', email='jack@github.com')

        for x in range(3):
            User.create(name='tom', email='jack@github.com')

        query = User.groupby(User.name).having(Fn.count(User.id) > 2).select(Fn.count(User.id), User.name)
        result = query.execute()
        assert result.count == 1L

        user = result.fetchone()

        assert user.count_of_id == 3L
        assert user.name == 'tom'

    def test_distinct(self):
        for x in range(2):
            User.create(name='jack', email='jack@github.com')

        for x in range(3):
            User.create(name='tom', email='jack@github.com')

        query = User.distinct().select(User.name)
        result = query.execute()
        assert result.count == 2L

    def test_modelobj_save(self):
        user = User(name="jack", email="jack@github.com")
        assert user.save()
        assert User.select().execute().count == 1L
        user.name = "li"
        assert user.save()
        assert User.at(1).select().execute().fetchone().name == "li"

        user = User(name='test!', email='haha@haha.com')
        id = user.save()
        assert id == 2L
        assert User.at(2).getone().name == 'test!'
        user.name = 'run a test!'
        rows_affected = user.save()
        assert rows_affected == 1L
        assert User.at(2).select(User.name).execute().fetchone().name == 'run a test!'

        user = User.at(1).select(User.name).execute().fetchone()
        try:
            user.name = 'hello!'
            user.save()
        except PrimaryKeyValueNotFound:
            pass

    def test_modelobj_destroy(self):
        self.create_data(3, table=1)
        user = User.at(1).select().execute().fetchone()
        assert user.destroy()
        assert User.at(1).select().execute().fetchone() is None

        user = User.at(2).select(User.name).execute().fetchone()
        try:
            user.destroy()
        except PrimaryKeyValueNotFound:
            pass

    # def test_select_without_primaryeky(self):
    #     self.create_data(3, table=1)
    #     user = User.at(1).select_without_primarykey(User.name).execute().fetchone()
    #     try:
    #         name = user.name
    #     except KeyError:
    #         pass

    def test_findone(self):
        self.create_data(3, table=1)
        user = User.findone(name="name1")
        assert User.id

    def test_findall(self):
        self.create_data(3, table=1)
        users = User.findall(User.name.like("name%"))
        assert len(list(users)) is 3
        users = User.findall(name="name1")
        assert len(list(users)) is 1

    def test_getone(self):
        self.create_data(3, table=1)
        user = User.at(1).getone()
        assert user.id == 1L
        assert User.at(100).getone() is None

    def test_getall(self):
        self.create_data(3, table=1)
        users = User.where(User.name=="name1").getall()
        assert len(list(users)) is 1

    def test_in_select(self):
        self.create_data(4)
        query = User.where(
            User.id._in(Post.select(Post.user_id))).select()
        result = query.execute()
        assert result.count == 4L

    def test_not_in_select(self):
        self.create_data(4)
        query = User.where(
            User.id.not_in(Post.select(Post.user_id))).select()
        result = query.execute()
        assert result.count == 0L

    def test_obj_in_model(self):

        self.create_data(4)
        user = User(name="name1", email="email1")
        assert user in User
        user1 = User.create(name="测试", email="ceshi@zhihu.com")
        assert user1 in User
        user2 = User.create(name=u"中文", email=u"zhongwen@zhihu.com")  # unicode
        assert user2 in User

    def test_limit(self):

        self.create_data(10)

        query = User.limit(4).select()
        result = query.execute()
        assert result.count == 4L

        assert len(tuple(User.limit(9, offset=1).getall())) is 9
        assert len(tuple(User.limit(100, offset=9).getall())) is 1


    def test_subquery(self):

        self.create_data(10)

        query = User.where(User.id._in(
            Post.select(Post.user_id)
        )).select()

        result = query.execute()

        assert result.count == 10L

        query = User.where(User.id.not_in(
            Post.select(Post.user_id)
        )).select()

        result = query.execute()

        assert result.count == 0L


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
        self.models = Models(Post, User)

    def test_where(self):
        assert self.models.where(User.id == Post.user_id).select().execute().count == 4L
        assert self.models.where(
            User.id == Post.user_id, User.id == 1
        ).select().execute().count == 1L

    def test_select(self):
        for post, user in self.models.where(
            User.id == Post.user_id
        ).select():
            assert user.id == post.user_id

        post, user = self.models.where(
            Post.post_id == User.id
        ).getone()

        assert user.id == post.post_id

    def test_groupby(self):
        query = self.models.groupby(User.name).select()
        result = query.execute()
        assert result.count == 4L

        query = self.models.groupby(User.name, Post.name).select()
        result = query.execute()
        assert result.count == 16L

    def test_having(self):
        query = self.models.groupby(User.name).having(Fn.count(User.id) >= 1).select()
        result = query.execute()
        assert result.count == 4L

        query = self.models.groupby(User.name).having(Fn.count(User.id) > 10).select()
        result = query.execute()
        assert result.count == 0

        query = self.models.groupby(User.name).having(Fn.count(User.id) == 4).select()
        result = query.execute()
        assert result.count == 4L

    def test_distinct(self):

        query = self.models.distinct().select(User.name)
        result = query.execute()
        assert result.count == 4L

    def test_update(self):
        assert self.models.where(
            User.id == Post.user_id
        ).update(User.name == "new").execute() == 4L

    def test_delete(self):
        assert self.models.where(User.id == Post.user_id).delete().execute() == 8L
        assert self.models.where(User.id == Post.user_id).select().execute().count == 0L

    def test_delete2(self):
        assert self.models.where(User.id == Post.user_id).delete(Post).execute() == 4L
        assert User.select().execute().count == 4L
        assert Post.select().execute().count == 0L

    def test_orderby(self):
        G = self.models.where(
            Post.post_id == User.id
        ).orderby(User.name, 1).getall()
        d = tuple(G)
        assert d == tuple(sorted(d, key=lambda x: x[1].name, reverse=True))

    def test_limit(self):
        query = self.models.where(
            (Post.user_id == User.id) & (User.id > 1)
        ).limit(4, offset=2).select()
        result = query.execute()
        assert result.count == 1L

    def test_getone(self):
        post, user = self.models.where(User.id == Post.user_id).getone()
        assert user.id == post.user_id

    def test_getall(self):
        g = self.models.where(User.id == Post.user_id).getall()
        for post, user in g:
            assert post.user_id == user.id


class TestJoinModel(Test):

    def setUp(self):
        super(TestJoinModel, self).setUp()
        self.create_data(10)

    def test_select(self):
        assert (Post & User).select().execute().count == 10L
        assert (Post & User).where(User.name == "name2").select().execute().count == 1L
        for post, user in (Post & User).select():
            assert post.post_id
            assert user.id
            assert post.user_id == user.id

    def test_delete(self):
        assert (Post & User).delete().execute() == 20L
        assert (Post & User).select().execute().count == 0L

    def test_delete2(self):
        assert (Post & User).delete(Post).execute() == 10L

    def test_update(self):
        assert (Post & User).where(
            User.name <= "name4"
        ).update(User.name == "hello").execute() == 5L
        assert (Post & User).where(
            User.name == "hello"
        ).update(Post.name == "good").execute() == 5L

    def test_foreignkey_exception(self):
        try:
            User & Post
        except ForeignKeyNotFound:
            pass
        else:
            raise Exception

    def test_findone(self):

        post, user = (Post & User).findone(User.name=="name1")
        assert user._id and post._id
        assert user._id == post.user_id
        assert user.name == "name1"

    def test_findall(self):

        g =  (Post & User).findall(User.name.like("name%"))

        i = 0

        for post, user in g:
            i+=1
            assert user.name and post._id
            assert user.id == post.user_id

        assert i == 10

    def test_getone(self):
        post, user = (Post & User).getone()
        assert post.user_id == user.id

    def test_getall(self):
        g = (Post & User).where(User.id <= 5).getall()
        assert len(tuple(g)) == 5

# select_result Tests

class TestSelect_result(Test):

    def test_count(self):
        self.create_data(5)
        assert User.select().execute().count == 5L

    def test_fetchone(self):
        self.create_data(4)
        user = User.at(1).getone()
        assert user.id == 1L

    def test_iter(self):
        self.create_data(4)
        i=0
        for user in User.where(User.id <= 3).select():
            i+=1
            assert user._id

        assert i == 3

    def test_fetchall(self):
        self.create_data(4)
        for user in User.select().execute().fetchall():
            assert user._id


class TestRuntime_:

    def test_reset_data(self):
        query = User.where(User.name == "hello")
        assert User.runtime.data['where']
        query = User.where(User.name == "x").select()
        for runtime_key, runtime_data in User.runtime.data.items():
            assert not runtime_data
        query2 = User.at(7).select()
        for runtime_key, runtime_data in User.runtime.data.items():
            assert not runtime_data


class TestFunctions(Test):

    def test_count(self):
        self.create_data(4)
        query = User.select(Fn.count(User.id))
        result = query.execute()
        assert result.count == 1L
        assert result.fetchone().count_of_id == 4L

        query = (Post & User).select(Fn.count(User.id), Fn.count(Post.post_id))
        result = query.execute()
        assert result.count == 1L
        post, user = result.fetchone()
        assert post.count_of_post_id == 4L
        assert user.count_of_id == 4L

    def test_max_min(self):
        self.create_data(4)
        query = User.select(Fn.max(User.id))
        result = query.execute()
        assert result.count == 1L
        user = result.fetchone()
        assert user.max_of_id == 4L

        query = User.select(Fn.min(User.id))
        result = query.execute()
        result = query.execute()
        assert result.count == 1L
        user = result.fetchone()
        assert user.min_of_id == 1L

        query = (Post & User).select(Fn.max(User.id), Fn.min(Post.post_id))
        result = query.execute()
        assert result.count == 1L
        post, user = result.fetchone()
        assert post.min_of_post_id == 1L
        assert user.max_of_id == 4L

    def test_sum(self):
        self.create_data(4)

        query = User.select(Fn.sum(User.id))
        result = query.execute()
        user = result.fetchone()
        assert user.sum_of_id == 10L

        query = (Post & User).select(Fn.sum(User.id), Fn.sum(Post.post_id))
        result = query.execute()
        assert result.count == 1L
        post, user = result.fetchone()
        assert post.sum_of_post_id == 10L
        assert user.sum_of_id == 10L

    def test_lcase_ucase(self):
        self.create_data(4, table=1)

        query = User.select(Fn.ucase(User.name), User.name)
        for user in query:
            assert user.name.upper() == user.ucase_of_name

        query = User.select(Fn.lcase(User.name), User.name)
        for user in query:
            assert user.name.lower() == user.lcase_of_name

    def test_shortcuts(self):
        self.create_data(4, table=1)
        assert User.count() == 4L
        assert User.sum(User.id) == 10L
        assert User.max(User.id) == 4L
        assert User.min(User.id) == 1L
