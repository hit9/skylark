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

# -------------------- {{{read config
cf = ConfigParser.ConfigParser()
cf.read('mysql.conf')

mysql_user = cf.get('MySQL', 'user')
mysql_passwd = cf.get('MySQL', 'passwd')
mysql_db = cf.get('MySQL', 'db')
# ----------------------- }}}

# -------------------------------------- {{{ create & drop tables

import MySQLdb

conn = MySQLdb.connect(db=mysql_db, user=mysql_user, passwd=mysql_passwd)

create_tbl_SQL = open("tables.sql").read()


def create_tables():
    conn.cursor().execute(create_tbl_SQL)


def drop_tables():
    conn.cursor().execute("drop table post, user")
# --------------------------------------- }}}


from models import User, Post, TestCustomTableName, TestTableName

sys.path.insert(0, '..')
from CURD import Database, Compiler, fn, distinct, sql


tostr = Compiler.tostr


class Test(object):  # classes inhrite from Test need database connection

    def setUp(self):
        create_tables()
        Database.config(db=mysql_db, user=mysql_user, passwd=mysql_passwd)

    def tearDown(self):
        drop_tables()

    def create_data(self, count, table=None):
        if table is 1:  # only create data in table `user`
            for i in range(1, count + 1):
                User.create(name='name' + str(i), email='email' + str(i))
        elif table is 2:  # only create data in table `post`
            for i in range(1, count + 1):
                Post.create(name='name' + str(i), user_id=count + 1 - i)
        else:  # both, default
            for i in range(1, count + 1):
                User.create(name='name' + str(i), email='email' + str(i))
            for i in range(1, count + 1):
                Post.create(name='name' + str(i), user_id=count + 1 - i)


class TestDatabase_:

    def test_config(self):
        Database.config(db=mysql_db, user=mysql_user, passwd=mysql_passwd,
                        charset='utf8', autocommit=True)

        assert Database.configs == {
            'db': mysql_db,
            'user': mysql_user,
            'passwd': mysql_passwd,
            'host': 'localhost',
            'port': 3306,
            'charset': 'utf8'
        }

        assert Database.autocommit is True


class TestDatabase(Test):

    def test_connect(self):
        Database.connect()
        assert Database.conn and Database.conn.open

    def test_execute(self):
        Database.execute('insert into user set user.name="test"')

    def test_change(self):
        conn = Database.conn
        Database.change(mysql_db)
        assert Database.conn is conn

        Database.config(db=mysql_db)
        Database.execute('insert into user set user.name="test"')
        assert Database.conn and Database.conn.open
        assert Database.conn is not conn


class TestField_:

    def test_name(self):
        assert User.name.name == 'name'
        assert User.email.name == 'email'
        assert Post.name.name == 'name'
        assert Post.user_id.name == 'user_id'

    def test_fullname(self):
        assert User.name.fullname == 'user.name'
        assert User.email.fullname == 'user.email'
        assert Post.name.fullname == 'post.name'
        assert Post.user_id.fullname == 'post.user_id'

    def test_is_primarykey(self):
        assert User.name.is_primarykey is False
        assert User.email.is_primarykey is False
        assert User.id.is_primarykey is True
        assert Post.post_id.is_primarykey is True

    def test_is_foreignkey(self):
        assert User.name.is_foreignkey is False
        assert User.email.is_foreignkey is False
        assert Post.post_id.is_foreignkey is False
        assert Post.user_id.is_foreignkey is True

    def test_alias(self):
        assert User.name.alias('uname').name == 'uname'
        assert User.name.alias('uname').fullname == 'user.name as uname'


class TestFunction_:

    def test_name(self):
        assert fn.count(User.id).name == 'count'
        assert fn.concat(User.name, 'hello').name == 'concat'
        assert fn.ucase(User.name).alias(
            'upper_cased_name').name == 'upper_cased_name'

    def test_fullname(self):
        assert fn.max(User.id).fullname == 'max(user.id)'
        assert fn.count(User.id).fullname == 'count(user.id)'
        assert fn.concat(User.name, 'hello') == "concat(user.name, 'hello')"


class TestExpr_:

    def test_and_or(self):
        expr1 = User.name == 'tom'
        expr2 = User.email == 'tom@github.com'
        assert tostr(expr1 & expr2) == (
            "(user.name = 'tom' and user.email = 'tom@github.com')"
        )
        assert tostr(expr1 | expr2) == (
            "(user.name = 'tom' or user.email = 'tom@github.com')")

    def test_operators(self):
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

    def test_unicode(self):
        expr = User.name == u'你好世界！'
        assert tostr(expr) == "user.name = '你好世界！'"


class TestModel_:

    def test_data(self):
        user1 = User(name='mark')
        user2 = User(User.email == 'mark@gmail.com')
        assert user1.data == {'name': 'mark'}
        assert user2.data == {'email': 'mark@gmail.com'}

    def test_modelobj_fieldname(self):
        user = User(name='name1')
        assert user.name == 'name1'

    def test_table_name(self):
        assert User.table_name == 'user'
        assert Post.table_name == 'post'
        assert TestTableName.table_name == 'test_table_name'
        assert TestCustomTableName.table_name == 'a_custom_table_name'

    def test_primarykey(self):
        assert User.primarykey is User.id
        assert Post.primarykey is Post.post_id
        assert User.primarykey.name == 'id'
        assert Post.primarykey.name == 'post_id'

    def test_operator_and(self):
        A = Post & User
        assert A.models == [Post, User]
        assert A.primarykey == [Post.post_id, User.id]


class TestModel(Test):

    def test_create(self):
        user1 = User.create(name='name1', email='email1')
        user2 = User.create(name='name2', email='email2')
        user3 = User.create(name='name3', email='email3')
        assert user1 and user2 and user3
        assert user1._id == 1L and user2._id == 2L and user3._id == 3L
        assert user1 in User and user2 in User and user3 in User
        assert User.at(1).getone().name == 'name1'
        assert User.at(2).getone().name == 'name2'
        assert User.at(3).getone().name == 'name3'

    def test_update(self):
        self.create_data(2, table=1)
        assert User.at(1).update(User.name == 'newname1').execute() == 1L
        assert User.at(2).update(name='newname2').execute() == 1L

        user = User.getone()
        assert user.name == 'newname1'

        query = User.update(email='newemail')
        assert query.execute() == 2L

    def test_select(self):
        self.create_data(4, table=4)
        query = User.at(1).select()
        results = query.execute()
        assert results.count == 1L
        user = results.one()
        assert user.id == 1L and user._in_db is True
        query = User.where(User.id < 3).select(User.name)
        results = query.execute()
        for user in results.all():
            assert user.name
        assert results.count == 2L

    def test_delete(self):
        self.create_data(4, table=1)
        assert User.at(1).delete().execute() == 1L
        assert User.where(
            (User.name == 'name1') | (User.name == 'name2')
        ).delete().execute() == 1L
        assert User.count() == 2L

    def test_where(self):
        self.create_data(3, table=1)
        assert User.where(User.id == 1) is User
        assert User.where(id=1) is User
        User.runtime.reset_data()
        assert User.where(User.name == 'name1').select().execute().count == 1
        assert User.where(User.name == 'name1',
                          User.email == 'email').select().execute().count == 0
        assert User.where(
            User.name.like('name%')).select().execute().count == 3L
        assert User.where(
            User.id.between(0, 4)).select().execute().count == 3L

    def test_expr_priority(self):
        assert User.create(name='jack', email='jack@gmail.com')
        query = User.where(
            (User.id < 0) & (
                (User.name == 'jack') | User.email == 'jack@gmail.com')
        ).select()
        results = query.execute()
        assert results.count == 0

    def test_at(self):
        self.create_data(3, table=1)
        assert User.at(1).select().execute().count == 1L
        assert User.at(-1).select().execute().count == 0
        assert User.at(1).select().execute().one().name == "name1"
        assert User.at(1).delete().execute()

    def test_orderby(self):
        self.create_data(3, table=1)
        users = User.orderby(
            User.id, desc=True).select(User.id, User.name).execute().all()
        user1, user2, user3 = tuple(users)
        assert user1.id > user2.id > user3.id

    def test_alias(self):
        self.create_data(3, table=1)
        query = User.having(sql('d') >= 3).select(User.id.alias('d'))
        results = query.execute()
        user = results.one()
        assert user.d == 3L

    def test_groupby(self):
        for x in range(2):
            User.create(name='jack', email='jack@github.com')
        for x in range(3):
            User.create(name='tom', email='jack@github.com')

        query = User.groupby(User.name).select(fn.count(User.id), User.name)

        for user, func in query:
            if user.name == 'jack':
                assert func.count == 2L
            elif user.name == 'tom':
                assert func.count == 3L

    def test_having(self):
        for x in range(2):
            User.create(name='jack', email='jack@github.com')
        for x in range(3):
            User.create(name='tom', email='jack@github.com')

        query = User.groupby(User.name).having(sql('count') > 2).select(
            fn.count(User.id).alias('count'), User.name)
        results = query.execute()
        assert results.count == 1L
        user, func = results.one()
        assert func.count == 3L and user.name == 'tom'

    def test_distinct(self):
        assert User.create(name='jack', email='jack@github.com')
        assert User.create(name='jack', email='jack@ele.me')
        assert User.create(name='wangchao', email='nz2324@126.com')
        assert User.create(name='hit9', email='nz2324@126.com')
        query = User.select(fn.count(distinct(User.name)))
        results = query.execute()
        func = results.one()
        assert func.count == 3L

        query = User.orderby(User.id).select(distinct(User.email))
        results = query.execute()
        assert tuple(results.tuples()) == (
            ('jack@github.com', ), ('jack@ele.me', ), ('nz2324@126.com', )
        )

        query = User.orderby(User.id).select(distinct(User.name), User.id)
        results = query.execute()
        assert tuple(results.dicts()) == (
            {'name': 'jack', 'id': 1L},
            {'name': 'jack', 'id': 2L},
            {'name': 'wangchao', 'id': 3L},
            {'name': 'hit9', 'id': 4L},
        )

    def test_model_inst_save(self):
        user = User(name='jack', email='jack@gmail.com')
        assert user.save() == 1L
        assert User.count() == 1L
        assert User.getone().name == 'jack'
        user.name = 'amy'
        assert user.save() == 1L
        assert User.findone(id=1).name == 'amy'


class TestSelectResults(Test):

    def test_one(self):
        self.create_data(3, table=1)
        query = User.orderby(User.id).select()
        results = query.execute()
        user = results.one()
        assert user.id == 1L

        query = User.at(3).select()
        results = query.execute()
        user = results.one()
        assert user.id == 3L

    def test_all(self):
        self.create_data(3, table=1)
        query = User.where(User.id > 1, User.id < 3).select()
        results = query.execute()
        assert results.count == 1L
        for user in results.all():
            assert user.id == 2L

        idx = 0
        for user in User.select():
            idx = idx + 1
            assert user.id == idx

    def test_tuples(self):
        self.create_data(3, table=1)
        query = User.select(User.id)
        results = query.execute()
        assert tuple(results.tuples()) == (
            (1L,),
            (2L,),
            (3L,),
        )

    def test_dicts(self):
        self.create_data(3)
        query = User.select()
        results = query.execute()
        assert tuple(results.dicts()) == (
            {'id': 1L, 'name': 'name1', 'email': 'email1'},
            {'id': 2L, 'name': 'name2', 'email': 'email2'},
            {'id': 3L, 'name': 'name3', 'email': 'email3'},
        )

        query = (Post & User).select()
        results = query.execute()
        assert tuple(results.dicts()) == (
            {'post_id': 1L, 'name': 'name1', 'user_id': 3L,
             'id': 3L, 'email': 'email3', 'user.name': 'name3'},
            {'post_id': 2L, 'name': 'name2', 'user_id': 2L,
             'id': 2L, 'email': 'email2', 'user.name': 'name2'},
            {'post_id': 3L, 'name': 'name3', 'user_id': 1L,
             'id': 1L, 'email': 'email1', 'user.name': 'name1'},
        )

    def test_func_only(self):
        self.create_data(3, table=1)
        query = User.select(fn.count(User.id))
        results = query.execute()
        func = results.one()
        assert func.count == 3L
        assert results.count == 1L

        query = User.at(2).select(fn.ucase(User.name).alias('uname'))
        results = query.execute()
        func = results.one()
        assert func.uname == 'NAME2'

        query = User.at(3).select(fn.concat(User.name, ' + ', 'hello'))
        results = query.execute()
        func = results.one()
        assert func.concat == 'name3 + hello'

    def test_func_and_inst(self):
        self.create_data(3, table=1)
        query = User.at(1).select(User.name, fn.ucase(User.name))
        results = query.execute()
        user, func = results.one()
        assert user.name == 'name1', func.ucase == 'NAME1'

        for user, func in User.select(User.name, fn.ucase(User.name)):
            assert user.name.upper() == func.ucase

    def test_inst_only(self):
        self.create_data(3)

        for post, user in (Post & User).select():
            assert post.user_id == user.id

    def test_examples(self):
        User.create(name='jack', email='jack@gmail.com')
        User.create(name='jack', email='jack1@gmail.com')
        User.create(name='amy', email='amy@gmail.com')
        # distinct
        query = User.select(distinct(User.name))
        results = query.execute()
        assert results.one().name == 'jack'
        assert results.one().name == 'amy'
        # groupby & orderby
        query = User.groupby(User.name).orderby(sql('count')).select(
            User.name, fn.count(User.id).alias('count'))
        results = query.execute()
        user, func = results.one()
        assert user.name == 'amy' and func.count == 1L
        user, func = results.one()
        assert user.name == 'jack' and func.count == 2L
