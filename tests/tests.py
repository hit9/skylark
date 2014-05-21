# coding=utf8

import os
import sys
import logging
logging.basicConfig(level=logging.INFO)
from decimal import Decimal

import toml

sys.path.insert(0, '..')
from skylark import Database, database, DBAPI_MAPPINGS, DatabaseType,\
    Model, fn, sql, distinct, PrimaryKeyValueNotFound, compiler, Models

from models import User, Post


dbapi_name = os.environ.get('DBAPI', 'MySQLdb')
dbapi = __import__(dbapi_name)
configs = toml.loads(open('conf.toml').read())[dbapi_name]

db_type_mappings = {
    'pymysql': 'mysql',
    'MySQLdb': 'mysql',
    'sqlite3': 'sqlite',
}

db_type = db_type_mappings[dbapi_name]

user_sql = open('%s.user.sql' % db_type).read()
post_sql = open('%s.post.sql' % db_type).read()


database.set_dbapi(dbapi)
logging.info('Using DBAPI %s' % dbapi_name)
database.config(**configs)
database.set_autocommit(True)


class Test(object):

    def setUp(self):
        database.execute(user_sql)
        database.execute(post_sql)

    def tearDown(self):
        database.execute("drop table t_post")
        database.execute("drop table t_user")

    def create_data(self, count, table=None):
        database.set_autocommit(False)
        # lots of insert in a transaction
        with database.transaction():
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
        database.set_autocommit(True)


class TestDatabase_:

    def setUp(self):
        self.database = DatabaseType()

    def test_alias(self):
        assert database is Database

    def __shouldnt_import(self, name):
        try:
            __import__(name)
            raise Exception
        except ImportError:
            pass

    def test_init(self):
        assert self.database.conn is None
        assert self.database.configs == {}
        assert self.database.dbapi.module.__name__ in DBAPI_MAPPINGS

        # test load orders
        name = self.database.dbapi.module.__name__

        if name == 'MySQLdb':
            assert __import__('MySQLdb')
        elif name == 'pymysql':
            assert __import__('pymysql')
            self.__shouldnt_import('MySQLdb')
        elif name == 'sqlite3':
            assert __import__('sqlite3')
            self.__shouldnt_import('MySQLdb')
            self.__shouldnt_import('pymysql')

    def test_set_dbapi(self):
        self.database.set_dbapi(dbapi)
        assert self.database.dbapi.module.__name__ == dbapi_name


class TestDatabase(Test):

    def setUp(self):
        self.database = DatabaseType()
        self.database.set_dbapi(dbapi)
        super(TestDatabase, self).setUp()

    def test_config(self):
        assert self.database.configs == {}
        self.database.config(**configs)
        assert self.database.configs
        assert not self.database.conn
        self.database.connect()
        assert self.database.conn
        self.database.config(**configs)
        assert not self.database.dbapi.conn_is_open(self.database.conn)

    def test_connect(self):
        assert self.database.conn is None
        self.database.config(**configs)
        conn1 = self.database.connect()
        conn2 = self.database.connect()
        assert conn1 is not conn2
        assert self.database.dbapi.conn_is_open(conn1)
        assert self.database.dbapi.conn_is_open(conn2)

    def test_get_conn(self):
        assert self.database.conn is None
        self.database.config(**configs)
        conn = self.database.get_conn()
        assert conn and self.database.dbapi.conn_is_open(conn)
        assert conn and self.database.dbapi.conn_is_alive(conn)
        conn1 = self.database.get_conn()
        assert conn1 is conn

    def test___del__(self):
        self.database.config(**configs)
        self.database.connect()
        conn = self.database.conn
        dbapi = self.database.dbapi
        del self.database
        conn = None
        assert not dbapi.conn_is_open(conn)

    def test_execute(self):
        self.database.config(**configs)
        cursor = self.database.execute(
            "insert into t_user (name, email) values ('jack', 'i@gmail.com')")
        assert cursor.lastrowid == 1

    def test_execute_sql(self):
        pass

    def change(self):
        self.database.configs(**configs)
        self.database.connect()
        old_conn = self.database.conn
        self.database.execute('create database skylarktests2')
        self.database.change('skylarktests2')
        assert self.database.configs != configs
        if db_type == 'mysql':
            self.database.conn is old_conn
        else:
            self.database.conn is not old_conn
            assert not self.database.dbapi.conn_is_open(old_conn)

    def test_transaction(self):
        db = self.database
        db.config(**configs)
        db.execute("insert into t_user (name, email) values ('j', 'j@i.com')")
        db.set_autocommit(False)
        t = db.transaction()
        try:
            db.execute("insert into t_user set x;")  # syntax error
        except Exception:
            t.rollback()
        else:
            raise Exception
        cursor = db.execute('select count(*) from t_user;')
        db.conn.commit()  # !important
        assert cursor.fetchone()[0] == 1

        with db.transaction() as t:
            db.execute(
                "insert into t_user (name, email) values ('a', 'a@b.com')")
            db.execute(
                "insert into t_user (name, email) values ('a', 'a@b.com')")
        cursor = db.execute('select count(*) from t_user')
        db.commit()
        assert cursor.fetchone()[0] == 3


class TestField_:

    def test_name(self):
        assert User.name.name == 'name'
        assert User.email.name == 'email'
        assert Post.name.name == 'name'
        assert Post.user_id.name == 'user_id'

    def test_fullname(self):
        assert User.name.fullname == 't_user.name'
        assert User.email.fullname == 't_user.email'
        assert Post.name.fullname == 't_post.name'
        assert Post.user_id.fullname == 't_post.user_id'

    def test_model(self):
        assert User.id.model is User
        assert User.name.model is User
        assert User.email.model is User
        assert Post.name.model is Post
        assert Post.user_id.model is Post

    def test_alias(self):
        fd = User.id.alias('user_id')
        assert fd.name == 'user_id'
        assert fd.inst is User.id


class TestPrimaryKey_:

    def test_is_primarykey(self):
        assert User.id.is_primarykey is True
        assert User.name.is_primarykey is False
        assert User.email.is_primarykey is False
        assert Post.post_id.is_primarykey is True
        assert Post.user_id.is_primarykey is False
        assert Post.name.is_primarykey is False


class TestForeignKey_:

    def test_is_foreignkey(self):
        assert User.id.is_foreignkey is False
        assert User.name.is_foreignkey is False
        assert User.email.is_foreignkey is False
        assert Post.post_id.is_foreignkey is False
        assert Post.name.is_foreignkey is False
        assert Post.user_id.is_foreignkey is True


class TestAlias_:

    def setUp(self):
        self._alias = User.name.alias('username')

    def test_name(self):
        assert self._alias.name == 'username'

    def test_inst(self):
        assert self._alias.inst is User.name


class TestAlias(Test):

    def test_function_alias(self):
        User.create(name='jack', email='jack@g.cn')
        User.create(name='jack', email='jack@gg.cn')
        User.create(name='amy', email='amy@g.cn')
        query = User.groupby(User.name).having(sql('count') >= 2).select(
            User.name, fn.count(User.id).alias('count')
        )
        result = query.execute()
        assert result.tuples()[0][1] == 2
        assert result.one().name == 'jack'

    def test_field_alias(self):
        User.create(name='jack', email='jack@g.cn')
        User.create(name='jack', email='jack@g.cn')
        User.create(name='amy', email='amy@g.cn')

        query = User.groupby(User.name).having(
            sql('em').like('%@g.cn')).orderby(User.id).select(
            User.name, User.email.alias('em'))

        assert [(user.name, user.em) for user in query] == [
            ('jack', 'jack@g.cn'), ('amy', 'amy@g.cn')
        ]


class TestModel_:

    def test_table_name(self):
        class MyModel(Model):
            pass
        assert MyModel.table_name == 'my_model'

        class Member(Model):
            pass
        assert Member.table_name == 'member'

        class Cat(Model):
            table_name = 'cute_cat'
        assert Cat.table_name == 'cute_cat'

    def test_table_prefix(self):
        class Users(Model):
            table_prefix = 't_'
        assert Users.table_name == 't_users'

        class CuteDog(Model):
            table_prefix = 'dd_'
        assert CuteDog.table_name == 'dd_cute_dog'

        class Dog(Model):
            table_name = 'custom_table_name'
            table_prefix = 'd_'
        assert Dog.table_name == 'd_custom_table_name'

    def test_table_prefix_is_inheritable(self):
        class X(Model):
            table_prefix = 't_'

        class A(X):
            pass

        class B(X):
            pass

        assert A.table_prefix is X.table_prefix
        assert B.table_prefix is X.table_prefix
        assert A.table_name == 't_a'
        assert B.table_name == 't_b'

    def test_primarykey(self):
        assert User.primarykey is User.id
        assert Post.primarykey is Post.post_id

    def test_fields(self):
        field_names = set(User.fields.keys())
        _field_names = set(('id', 'name', 'email'))
        assert field_names == _field_names
        field_names = set(Post.fields.keys())
        _field_names = set(('post_id', 'name', 'user_id'))
        assert field_names == _field_names


class TestModel(Test):

    def test_insert(self):
        query = User.insert(name='jack', email='jack@gmail.com')
        assert query.execute() == 1
        assert User.count() == 1
        user = User.getone()
        assert user.name == 'jack' and user.email == 'jack@gmail.com'

    def test_update(self):
        user = User.create(name='jack', email='jack@gmail.com')
        assert user.id == 1
        assert user.name == 'jack'
        assert user.email == 'jack@gmail.com'
        assert User.count() == 1

        query = User.at(1).update(email='jack@g.com')
        rows_affected = query.execute()
        assert rows_affected == 1
        user = User.getone()
        assert user.id == 1 and user.email == 'jack@g.com'

    def test_inst_in_model(self):
        user = User.create(name='jack', email='jack@gmail.com')

        # inst with `_in_db=True` won't call db to run a query
        database.conn.close()  # close conn to test if any sql was executed
        database.conn = None
        assert user in User
        assert database.conn is None

        # inst without `_in_db=True` call a query
        assert User(name='amy') not in User
        assert database.conn is not None

    def test_select(self):
        User.create(name='jack', email='jack@gmail.com')
        User.create(name='amy', email='amy@gmail.com')
        User.create(name='tom', email='tom@gmail.com')
        ### select all fields
        query = User.select()
        result = query.execute()
        assert result.count == 3
        for user in result.all():
            assert '%s@gmail.com' % user.name == user.email
        ### select part fields
        query = User.select(User.name)
        result = query.execute()
        assert result.count == 3
        jack = result.one()
        assert jack.name == 'jack'
        amy = result.one()
        assert amy.name == 'amy'
        tom = result.one()
        assert tom.name == 'tom'
        assert result.one() is None
        ### select with where
        query = User.where(name='jack').select()
        result = query.execute()
        assert result.count == 1
        assert result.one().name == 'jack'

    def test_delete(self):
        User.create(name='jack', email='jack@gmail.com')
        User.create(name='amy', email='amy@gmail.com')
        query = User.at(3).delete()
        rows_affected = query.execute()
        assert rows_affected == 0
        query = User.at(1).delete()
        rows_affected = query.execute()
        assert rows_affected == 1
        assert User.count() == 1

    def test_create(self):
        user = User.create(name='jack', email='jack@gmail.com')
        assert user.data == {
            'name': 'jack', 'email': 'jack@gmail.com', 'id': 1
        }
        assert user in User
        assert user._in_db
        assert User.count() == 1

        _user = User.getone()
        assert _user.data == user.data
        assert _user._in_db

    def test_where(self):
        User.create(name='jack', email='jack@gmail.com')
        User.create(name='amy', email='amy@gmail.com')
        User.create(name='tom', email='tom@gmail.com')

        assert ['jack'] == [
            user.name for user in User.where(name='jack').select()]

        assert [1] == [
            user.id for user in User.where(id=1).select()
        ]

        assert ['tom'] == [
            user.name for user in User.where(User.name.like('t%')).select()]

    def test_at(self):
        User.create(name='jack', email='jack@gmail.com')
        assert User.at(1).getone().name == 'jack'
        assert User.at(2).getone() is None
        assert User.at(-1).select().execute().count == 0

    def test_orderby(self):
        User.create(name='jack', email='jack@gmail.com')
        User.create(name='amy', email='amy@gmail.com')
        User.create(name='tom', email='tom@gmail.com')

        query = User.orderby(User.id).select()
        result = query.execute()
        users = result.all()
        assert [(user.id, user.name) for user in users] == [
            (1, 'jack'), (2, 'amy'), (3, 'tom')
        ]

        query = User.orderby(User.id, desc=True).select()
        result = query.execute()
        users = result.all()
        assert [(user.id, user.name) for user in users] == [
            (3, 'tom'), (2, 'amy'), (1, 'jack')
        ]

    def test_groupby(self):
        for x in range(2):
            User.create(name='jack', email='jack@github.com')
        for x in range(3):
            User.create(name='tom', email='jack@github.com')

        query = User.groupby(User.name).orderby(sql('count')).select(
            fn.count(User.id).alias('count'), User.name)
        result = query.execute()
        assert result.tuples() == (
            (2, 'jack'), (3, 'tom')
        )

    def test_having(self):
        for x in range(2):
            User.create(name='jack', email='jack@github.com')
        for x in range(3):
            User.create(name='tom', email='jack@github.com')

        query = User.groupby(User.name).having(sql('count') > 2).select(
            fn.count(User.id).alias('count'), User.name)
        result = query.execute()
        user = result.one()
        count = result.tuples()[0][0]
        assert count == 3 and user.name == 'tom'

    def test_limit(self):
        self.create_data(10)
        query = User.limit(4).select()
        result = query.execute()
        assert result.count == 4
        query = User.limit(9, offset=1).select(User.id)
        result = query.execute()
        assert result.count == 9
        query = User.limit(100, offset=9).select(User.id)
        result = query.execute()
        assert result.count == 1

    def test_distinct(self):
        assert User.create(name='jack', email='jack@github.com')
        assert User.create(name='jack', email='jack@ele.me')
        assert User.create(name='wangchao', email='nz2324@126.com')
        assert User.create(name='hit9', email='nz2324@126.com')
        query = User.select(fn.count(distinct(User.name)))
        result = query.execute()
        count = result.tuples()[0][0]
        assert count == 3

        query = User.orderby(User.id).select(distinct(User.email))
        result = query.execute()
        assert result.tuples() == (
            ('jack@github.com',), ('jack@ele.me',), ('nz2324@126.com', )
        )

        emails = [user.email for user in result.all()]
        assert len(emails) == len(set(emails))

        query = User.orderby(User.id).select(distinct(User.name, User.email))
        try:
            result = query.execute()
        except Exception:  # should raise an error
            pass
        else:
            raise Exception

        query = User.orderby(User.id).select(distinct(User.name), User.email)
        result = query.execute()
        assert result.count == 4

    def test_findone(self):
        assert User.create(name='jack', email='jack@gmail.com')
        assert User.create(name='amy', email='amy@gmail.com')
        jack = User.findone(name='jack')
        amy = User.findone(name='amy')
        assert jack.email == 'jack@gmail.com'
        assert amy.email == 'amy@gmail.com'

    def test_findall(self):
        assert User.create(name='jack', email='jack@gmail.com')
        assert User.create(name='amy', email='amy@gmail.com')

        users = User.findall(User.email.like('%@gmail.com'))
        assert ['jack', 'amy'] == [user.name for user in users]

    def test_getone(self):
        assert User.create(name='jack', email='jack@gmail.com')
        assert User.create(name='amy', email='amy@gmail.com')

        user = User.at(1).getone()
        assert user.name == 'jack' and user.id == 1

        user = User.at(10).getone()
        assert user is None

    def test_getall(self):
        assert User.create(name='jack', email='jack@gmail.com')
        assert User.create(name='amy', email='amy@gmail.com')
        users = User.getall()
        assert ['jack', 'amy'] == [user.name for user in users]

    def test_inst_save(self):
        user = User(name='jack', email='jack@gmail.com')
        assert user.save() == 1  # insert
        assert user._in_db and user in User
        assert User.count() == 1
        assert User.getone().name == 'jack'
        user.email = 'hack@gmail.com'
        assert user.save() == 1  # update
        assert User.getone().email == 'hack@gmail.com'
        # test inst._cache
        assert user.save() == 0  # nothing change

        user = User(name='jack', email='jack@g.cn')
        user.set_in_db(True)
        try:
            user.save()
        except PrimaryKeyValueNotFound:
            pass
        else:
            raise Exception

    def test_inst_desctroy(self):
        user = User(name='jack', email='jack@gmail.com')
        assert user.save() == 1  # insert
        assert user.destroy() == 1  # delete
        user = User.create(name='i', email='b')
        assert user.destroy() == 1  # rows_affected
        user = User(name='a', email='b')
        assert user.destroy() is None

    def test_subquery(self):
        self.create_data(10)

        query = User.where(User.id._in(Post.select(Post.user_id))).select()
        result = query.execute()
        assert result.count == 10

        query = User.where(id=(Post.select(fn.max(Post.user_id)))).select()
        result = query.execute()
        assert result.count == 1
        assert result.one().id == 10

        query = User.where(
            User.id < Post.select(fn.min(Post.user_id))).select()
        result = query.execute()
        assert result.count == 0

    def test_transaction(self):
        database.set_autocommit(False)
        with database.transaction() as t:
            User.create(name='jack', email='jack@gmail.com')

        with database.transaction() as t:
            try:
                User.create(name='amy', id=1)
            except:
                t.rollback()
        database.set_autocommit(True)
        assert User.count() == 1

    def test_join(self):
        User.create(name='jack', email='jack@gmail.com')
        User.create(name='amy', email='amy@gmail.com')
        Post.create(name='Hello world', user_id=1)
        query = User.join(Post).select(User.name)
        result = query.execute()
        assert result.count == 1
        user = result.one()
        assert user.name == 'jack'

    def test_left_join(self):
        User.create(name='jack', email='jack@gmail.com')
        User.create(name='amy', email='amy@gmail.com')
        Post.create(name='Hello world', user_id=1)
        query = User.left_join(Post).select(User.name)
        result = query.execute()
        assert result.count == 2

    def test_right_join(self):
        if db_type != 'sqlite':  # sqlite3 current not support right join
            User.create(name='jack', email='jack@gmail.com')
            User.create(name='amy', email='amy@gmail.com')
            Post.create(name='Hello world', user_id=1)
            query = Post.right_join(User).select()
            result = query.execute()
            assert result.count == 2


class TestSelectResult(Test):

    def test_count(self):
        self.create_data(4, table=1)
        query = User.where(User.id > 4).select()
        result = query.execute()
        assert result.count == 0
        query = User.where(User.id > 3).select()
        result = query.execute()
        assert result.count == 1

    def test_one(self):
        self.create_data(3, table=1)
        query = User.orderby(User.id).select()
        result = query.execute()
        user = result.one()
        assert user.id == 1

    def test_all(self):
        self.create_data(3, table=1)
        query = User.orderby(User.id).select()
        result = query.execute()
        users = result.all()
        assert [user.id for user in users] == [1, 2, 3]

    def test_tuples(self):
        assert User.create(name='jack', email='jack@gmail.com')
        assert User.create(name='amy', email='amy@gmail.com')
        assert User.create(name='tom', email='tom@gmail.com')
        query = User.select(User.id)
        result = query.execute()
        assert result.tuples() == ((1,), (2,), (3,))

    def test_selected_inst_in_db(self):
        self.create_data(4, table=1)
        query = User.select()
        result = query.execute()
        user = result.one()
        assert user._in_db is True
        users = result.all()
        for user in users:
            assert user._in_db is True

    def test_distinct_nodes(self):
        assert User.create(name='jack', email='jack@gmail.com')
        assert User.create(name='amy', email='amy@gmail.com')
        assert User.create(name='amy', email='amy@gmail.com')
        assert User.create(name='tom', email='tom@gmail.com')

        query = User.select(distinct(User.name))
        result = query.execute()
        users = result.all()
        assert [user.name for user in users] == ['jack', 'amy', 'tom']

    def test_a_lot_of_insert_in_transaction(self):
        database.set_autocommit(False)
        with database.transaction():
            for i in range(1000):
                User.create(name=str(i), email=str(i))
        database.set_autocommit(True)


class TestOperators(Test):

    def test_expr_priority(self):
        assert User.create(name='jack', email='jack@gmail.com')
        # query should be:
        #  "(id < 0) and (name='jack' or email='jack@gmail.com')" => 0 rows
        # but not be:
        #  "id < 0 and name = 'jack' or email='jack@gmail.com'" => 1 rows
        query = User.where(
            (User.id < 0) & (
                (User.name == 'jack') | (User.email == 'jack@gmail.com')
            )
        ).select()
        assert query.execute().count == 0  # not 1

        query = User.where(
            (User.id < 0) & (
                User.name == 'jack') | (User.email == 'jack@gmail.com')
        ).select()
        assert query.execute().count == 1

    def test_bitwise_operator(self):
        assert User.create(name='jack', email='jack@gmail.com')
        if db_type != 'sqlite':  # sqlite3 dosen't know operator '^'
            query = User.select(User.id.op('^')(1))
            result = query.execute()
            assert result.tuples()[0][0] == 0

        query = User.select(User.id.op('&')(0))
        result = query.execute()
        assert result.tuples()[0][0] == 0

        query = User.select(sql('').op('~-')(User.id))
        result = query.execute()
        assert result.tuples()[0][0] == 0


class TestOperators_:

    def test_operators(self):
        def eq(expr, string, data):
            string = string.replace('?', database.dbapi.placeholder)
            sq1 = compiler.sql(expr)
            sq2 = sql(string, *data)
            return sq1.literal == sq2.literal and sq1.params == sq2.params

        assert eq(User.id < 1, 't_user.id < ?', (1,))
        assert eq(User.id <= 1, 't_user.id <= ?', (1,))
        assert eq(User.id > 1, 't_user.id > ?', (1,))
        assert eq(User.id >= 1, 't_user.id >= ?', (1,))
        assert eq(User.id == 1, 't_user.id = ?', (1,))
        assert eq(User.id != 1, 't_user.id <> ?', (1,))
        assert eq(User.id + 1, 't_user.id + ?', (1,))
        assert eq(User.id - 1, 't_user.id - ?', (1,))
        assert eq(User.id * 1, 't_user.id * ?', (1,))
        assert eq(User.id / 1, 't_user.id / ?', (1,))
        assert eq(User.id % 1, 't_user.id % ?', (1,))
        assert eq((User.id > 1) & (User.id < 4),
                  '(t_user.id > ? and t_user.id < ?)', (1, 4))
        assert eq((User.id > 1) | (User.id < 4),
                  '(t_user.id > ? or t_user.id < ?)', (1, 4))
        assert eq(1 + User.id, '? + t_user.id', (1,))
        assert eq(1 - User.id, '? - t_user.id', (1,))
        assert eq(1 * User.id, '? * t_user.id', (1,))
        assert eq(1 / User.id, '? / t_user.id', (1,))
        assert eq(1 % User.id, '? % t_user.id', (1,))
        assert eq(1 & User.id, '(? and t_user.id)', (1,))
        assert eq(1 | User.id, '(? or t_user.id)', (1,))
        assert eq(User.name.like('%a'), 't_user.name like ?', ('%a',))
        assert eq(User.id._in(1, 2), 't_user.id in (?, ?)', (1, 2))
        assert eq(User.id.not_in(1, 2), 't_user.id not in (?, ?)', (1, 2))
        assert eq(User.id.between(1, 2), 't_user.id between ? and ?', (1, 2))
        # custom bitwise ops
        assert eq(User.id.op('^')(1), 't_user.id ^ ?', (1,))
        assert eq(User.id.op('&')(1), 't_user.id & ?', (1,))
        assert eq(sql('').op('~')(User.id), ' ~ t_user.id', tuple())


class TestCommonFunctions(Test):

    def test_count(self):
        self.create_data(4)
        assert User.count() == 4
        assert Post.count() == 4
        query = User.select(fn.count(User.id))
        result = query.execute()
        assert result.count == 1
        assert result.tuples()[0][0] == 4

    def test_max(self):
        self.create_data(4)
        query = User.select(fn.max(User.id))
        result = query.execute()
        assert result.count == 1
        assert result.tuples()[0][0] == 4

    def test_min(self):
        self.create_data(4)
        query = User.where(User.id > 2).select(fn.min(User.id))
        result = query.execute()
        assert result.count == 1
        assert result.tuples()[0][0] == 3

    def test_sum(self):
        self.create_data(4)
        query = User.select(fn.sum(User.id))
        result = query.execute()
        assert result.count == 1
        assert result.tuples()[0][0] == 10
        assert User.sum(User.id) == 10

    def test_avg(self):
        self.create_data(4)
        query = User.select(fn.avg(User.id))
        result = query.execute()
        assert result.count == 1
        assert result.tuples()[0][0] == User.avg(User.id) == Decimal('2.5')

    def test_concat(self):
        assert User.create(name='jack', email='jack@gmail.com')
        if db_type != 'sqlite':  # in sqlite, `||` is concat
            query = User.select(fn.concat(User.name, ' + ', User.email))
            result = query.execute()
            assert result.tuples()[0][0] == 'jack + jack@gmail.com'
            query = User.at(1).update(name=fn.concat(User.name, ':'))
            result = query.execute()
            assert result == 1
            jack = User.at(1).getone()
            assert jack.name == 'jack:'
        else:
            query = User.select(User.name.op('||')(' + ').op('||')(User.email))
            result = query.execute()
            assert result.tuples()[0][0] == 'jack + jack@gmail.com'
            query = User.at(1).update(name=User.name.op('||')(':'))
            result = query.execute()
            assert result == 1
            jack = User.at(1).getone()
            assert jack.name == 'jack:'


class TestMultiModels(Test):

    def setUp(self):
        super(TestMultiModels, self).setUp()
        self.create_data(4)
        self.models = Models(Post, User)

    def test_where(self):
        assert self.models.where(
            User.id == Post.user_id).select().execute().count == 4
        assert self.models.where(
            User.id == Post.user_id, User.id == 1
        ).select().execute().count == 1

    def test_select(self):
        for post, user in self.models.where(
            User.id == Post.user_id
        ).select():
            assert user.id == post.user_id

        post, user = self.models.where(
            Post.post_id == User.id
        ).getone()

        assert user.id == post.post_id == 1

    def test_groupby(self):
        query = self.models.groupby(User.name).select()
        results = query.execute()
        assert results.count == 4

        query = self.models.groupby(User.name, Post.name).select()
        result = query.execute()
        assert result.count == 16

    def test_having(self):
        query = self.models.groupby(
            User.name).having(fn.count(User.id) >= 1).select()
        results = query.execute()
        assert results.count == 4

        query = self.models.groupby(
            User.name).having(fn.count(User.id) > 4).select()
        results = query.execute()
        assert results.count == 0

        query = self.models.groupby(
            User.name).having(fn.count(User.id) == 4).select()
        results = query.execute()
        assert results.count == 4   # 16 / 4 =4

    def test_distinct(self):
        query = self.models.select(distinct(User.name))
        result = query.execute()
        assert result.count == 4

    def test_orderby(self):
        g = self.models.where(
            Post.post_id == User.id
        ).orderby(User.name, desc=True).getall()
        d = tuple(g)
        assert d == tuple(sorted(d, key=lambda x: x[1].name, reverse=True))

    def test_limit(self):
        query = self.models.where(
            (Post.user_id == User.id) & (User.id > 1)
        ).limit(4, offset=2).select()
        result = query.execute()
        assert result.count == 1

    def test_getone(self):
        post, user = self.models.where(User.id == Post.user_id).getone()
        assert user.id == post.user_id

    def test_getall(self):
        g = self.models.where(User.id == Post.user_id).getall()
        for post, user in g:
            assert post.user_id == user.id
