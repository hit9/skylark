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
import logging
logging.basicConfig(level=logging.INFO)

if sys.hexversion < 0x03000000:
    import ConfigParser
else:
    import configparser as ConfigParser

# -------------------- {{{read config
cf = ConfigParser.ConfigParser()
cf.read('mysql.conf')

mysql_user = cf.get('MySQL', 'user')
mysql_passwd = cf.get('MySQL', 'passwd')
mysql_db = cf.get('MySQL', 'db')
# ----------------------- }}}

# -------------------------------------- {{{ create & drop tables

try:  # try to use MySQLdb, else pymysql
    import MySQLdb as mysql
    logging.info('Using MySQLdb')
except ImportError:
    import pymysql as mysql
    logging.info('Using PyMySQL')

conn = mysql.connect(db=mysql_db, user=mysql_user, passwd=mysql_passwd)

create_tbl_SQL = open("tables.sql").read()


def create_tables():
    conn.cursor().execute(create_tbl_SQL)


def drop_tables():
    conn.cursor().execute("drop table post, user")
# --------------------------------------- }}}

from decimal import Decimal

from models import User, Post, TestCustomTableName, TestTableName

sys.path.insert(0, '..')
from skylark import Database, Compiler, fn, distinct, sql, \
    PrimaryKeyValueNotFound, ForeignKeyNotFound, \
    Models, conn_is_up


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
        assert conn_is_up(Database.conn)

    def test_execute(self):
        cursor = Database.execute('insert into user set user.name="test"')
        assert cursor

    def test_change(self):
        conn = Database.conn
        Database.change(mysql_db)
        assert Database.conn is conn

        Database.config(db=mysql_db)
        Database.execute('insert into user set user.name="test"')
        assert conn_is_up(Database.conn)
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
        assert user1._id == 1 and user2._id == 2 and user3._id == 3
        assert user1 in User and user2 in User and user3 in User
        assert User.at(1).getone().name == 'name1'
        assert User.at(2).getone().name == 'name2'
        assert User.at(3).getone().name == 'name3'

    def test_update(self):
        self.create_data(2, table=1)
        assert User.at(1).update(User.name == 'newname1').execute() == 1
        assert User.at(2).update(name='newname2').execute() == 1

        user = User.getone()
        assert user.name == 'newname1'

        query = User.update(email='newemail')
        assert query.execute() == 2

    def test_select(self):
        self.create_data(4, table=4)
        query = User.at(1).select()
        results = query.execute()
        assert results.count == 1
        user = results.one()
        assert user.id == 1 and user._in_db is True
        query = User.where(User.id < 3).select(User.name)
        results = query.execute()
        for user in results.all():
            assert user.name
        assert results.count == 2

    def test_delete(self):
        self.create_data(4, table=1)
        assert User.at(1).delete().execute() == 1
        assert User.where(
            (User.name == 'name1') | (User.name == 'name2')
        ).delete().execute() == 1
        assert User.count() == 2

    def test_where(self):
        self.create_data(3, table=1)
        assert User.where(User.id == 1) is User
        assert User.where(id=1) is User
        User.runtime.reset_data()
        assert User.where(User.name == 'name1').select().execute().count == 1
        assert User.where(User.name == 'name1',
                          User.email == 'email').select().execute().count == 0
        assert User.where(
            User.name.like('name%')).select().execute().count == 3
        assert User.where(
            User.id.between(0, 4)).select().execute().count == 3

    def test_expr_priority(self):
        assert User.create(name='jack', email='jack@gmail.com')
        query = User.where(
            (User.id < 0) & (
                (User.name == 'jack') | (User.email == 'jack@gmail.com'))
        ).select()
        results = query.execute()
        assert results.count == 0

    def test_at(self):
        self.create_data(3, table=1)
        assert User.at(1).select().execute().count == 1
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
        assert user.d == 3

    def test_groupby(self):
        for x in range(2):
            User.create(name='jack', email='jack@github.com')
        for x in range(3):
            User.create(name='tom', email='jack@github.com')

        query = User.groupby(User.name).select(fn.count(User.id), User.name)

        for user, func in query:
            if user.name == 'jack':
                assert func.count == 2
            elif user.name == 'tom':
                assert func.count == 3

    def test_having(self):
        for x in range(2):
            User.create(name='jack', email='jack@github.com')
        for x in range(3):
            User.create(name='tom', email='jack@github.com')

        query = User.groupby(User.name).having(sql('count') > 2).select(
            fn.count(User.id).alias('count'), User.name)
        results = query.execute()
        assert results.count == 1
        user, func = results.one()
        assert func.count == 3 and user.name == 'tom'

    def test_distinct(self):
        assert User.create(name='jack', email='jack@github.com')
        assert User.create(name='jack', email='jack@ele.me')
        assert User.create(name='wangchao', email='nz2324@126.com')
        assert User.create(name='hit9', email='nz2324@126.com')
        query = User.select(fn.count(distinct(User.name)))
        results = query.execute()
        func = results.one()
        assert func.count == 3

        query = User.orderby(User.id).select(distinct(User.email))
        results = query.execute()
        assert tuple(results.tuples()) == (
            ('jack@github.com', ), ('jack@ele.me', ), ('nz2324@126.com', )
        )

        query = User.orderby(User.id).select(distinct(User.name), User.id)
        results = query.execute()
        assert tuple(results.dicts()) == (
            {'name': 'jack', 'id': 1},
            {'name': 'jack', 'id': 2},
            {'name': 'wangchao', 'id': 3},
            {'name': 'hit9', 'id': 4},
        )

    def test_model_inst_save(self):
        user = User(name='jack', email='jack@gmail.com')
        assert user.save() == 1
        assert User.count() == 1
        assert User.getone().name == 'jack'
        user.name = 'amy'
        assert user.save() == 1
        assert User.findone(id=1).name == 'amy'

        user = User(name='test!', email='haha@haha.com')
        id = user.save()
        assert id == 2
        assert User.at(2).getone().name == 'test!'
        user.name = 'run a test!'
        rows_affected = user.save()
        assert rows_affected == 1
        query = User.at(2).select(User.name)
        results = query.execute()
        user = results.one()
        try:
            user.name = 'hello'
            user.save()
        except PrimaryKeyValueNotFound:
            pass

    def test_instance_destroy(self):
        self.create_data(3, table=1)
        user = User.at(1).getone()
        assert user.destroy()
        assert user._in_db is False
        assert User.at(1).getone() is None

        user = User.at(2).select(User.name).execute().one()
        try:
            user.destroy()
        except PrimaryKeyValueNotFound:
            pass

    def test_findone(self):
        self.create_data(3, table=1)
        user = User.findone(name='name1')
        assert user.id == 1

    def test_findall(self):
        self.create_data(3, table=1)
        users = User.findall(User.name.like('name%'))
        assert len(list(users)) == 3
        users = User.findall(name='name1')
        assert len(list(users)) == 1

    def test_getone(self):
        self.create_data(3, table=1)
        user = User.at(1).getone()
        assert user.name == 'name1' and user.id == 1
        assert User.at(100).getone() is None

    def test_getall(self):
        self.create_data(3, table=1)
        users = User.where(User.name == 'name1').getall()
        assert len(list(users)) == 1

    def test_in_select(self):
        self.create_data(4)

        query = User.where(User.id._in(Post.select(Post.user_id))).select()
        results = query.execute()
        assert results.count == 4

    def test_not_in_select(self):
        self.create_data(4)
        query = User.where(
            User.id.not_in(Post.select(Post.user_id))
        ).select()
        results = query.execute()
        assert results.count == 0

    def test_instance_in_models(self):
        self.create_data(4)
        user = User(name='helo', email='abc')
        assert user not in User
        assert user.save() == 5
        assert user in User
        user = User(name='name1')
        assert user in User
        user = User(name=u'中文')
        assert user not in User

    def test_limit(self):
        self.create_data(10)
        query = User.limit(4).select()
        results = query.execute()
        assert results.count == 4
        assert len(tuple(User.limit(9, offset=1).getall())) is 9
        assert len(tuple(User.limit(100, offset=9).getall())) is 1

    def test_subquery(self):
        self.create_data(10)

        query = User.where(User.id._in(Post.select(Post.user_id))).select()
        results = query.execute()
        assert results.count == 10


class TestSelectResults(Test):

    def test_one(self):
        self.create_data(3, table=1)
        query = User.orderby(User.id).select()
        results = query.execute()
        user = results.one()
        assert user.id == 1

        query = User.at(3).select()
        results = query.execute()
        user = results.one()
        assert user.id == 3

    def test_all(self):
        self.create_data(3, table=1)
        query = User.where(User.id > 1, User.id < 3).select()
        results = query.execute()
        assert results.count == 1
        for user in results.all():
            assert user.id == 2

        idx = 0
        for user in User.select():
            idx = idx + 1
            assert user.id == idx

    def test_tuples(self):
        self.create_data(3, table=1)
        query = User.select(User.id)
        results = query.execute()
        assert tuple(results.tuples()) == (
            (1,),
            (2,),
            (3,),
        )

    def test_dicts(self):
        self.create_data(3)
        query = User.select()
        results = query.execute()
        assert tuple(results.dicts()) == (
            {'id': 1, 'name': 'name1', 'email': 'email1'},
            {'id': 2, 'name': 'name2', 'email': 'email2'},
            {'id': 3, 'name': 'name3', 'email': 'email3'},
        )

        query = (Post & User).orderby(User.id).select()
        results = query.execute()
        assert tuple(results.dicts()) == (
            {'post_id': 3, 'name': 'name3', 'user_id': 1,
             'id': 1, 'email': 'email1', 'user.name': 'name1'},
            {'post_id': 2, 'name': 'name2', 'user_id': 2,
             'id': 2, 'email': 'email2', 'user.name': 'name2'},
            {'post_id': 1, 'name': 'name1', 'user_id': 3,
             'id': 3, 'email': 'email3', 'user.name': 'name3'},
        )

    def test_func_only(self):
        self.create_data(3, table=1)
        query = User.select(fn.count(User.id))
        results = query.execute()
        func = results.one()
        assert func.count == 3
        assert results.count == 1

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

    def test_iter(self):
        self.create_data(4)
        i = 0
        for user in User.where(User.id < 3).select(User.id):
            i = i + 1
            assert user.id == i

        assert i == 2

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
        assert user.name == 'amy' and func.count == 1
        user, func = results.one()
        assert user.name == 'jack' and func.count == 2


class TestRuntime_:

    def test_reset_data(self):
        User.where(User.name == 'hello')
        assert User.runtime.data['where']
        User.where(User.name == 'x').select()
        for runtime_key, runtime_data in User.runtime.data.items():
            assert not runtime_data
        User.at(7).select()
        for runtime_key, runtime_data in User.runtime.data.items():
            assert not runtime_data


class TestCommonFunctions(Test):

    def test_count(self):
        self.create_data(4)
        assert User.count() == 4
        query = (Post & User).select(
            fn.count(User.id).alias('count_user_id'),
            fn.count(Post.post_id).alias('count_post_id'))
        results = query.execute()
        assert results.count == 1
        func = results.one()
        assert func.count_user_id == 4
        assert func.count_post_id == 4

    def test_max_min(self):
        self.create_data(4, table=1)
        assert User.max(User.id) == 4
        assert User.min(User.id) == 1

    def test_sum(self):
        self.create_data(4, table=1)
        assert User.sum(User.id) == 10

    def test_lcase_ucase(self):
        self.create_data(4, table=1)
        query = User.select(fn.ucase(User.name), User.name)
        for user, func in query:
            assert user.name.upper() == func.ucase

        query = User.select(fn.lcase(User.name), User.name)
        for user, func in query:
            assert user.name.lower() == func.lcase

    def test_avg(self):
        self.create_data(4, table=1)
        assert User.avg(User.id) == Decimal('2.5')

    def test_concat(self):
        self.create_data(4, table=1)
        query = User.select(fn.concat(User.name, '+', User.email))

        idx = 0
        for func in query:
            idx = idx + 1
            assert func.concat == 'name%d+email%d' % (idx, idx)

        query = User.at(1).update(name=fn.concat(User.email, User.id))
        assert query.execute() == 1
        assert User.at(1).getone().name == 'email11'


class TestModels_:

    def setUp(self):
        self.models = Models(User, Post)

    def test_models_table_name(self):
        assert self.models.table_name == "user, post"

    def test_models_primarykey(self):
        assert self.models.primarykey == [User.id, Post.post_id]


class TestModels(Test):

    def setUp(self):
        super(TestModels, self).setUp()
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

        assert user.id == post.post_id

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

    def test_update(self):
        assert self.models.where(
            User.id == Post.user_id
        ).update(User.name == 'new').execute() == 4

        User.at(1).getone().name == 'new'

    def test_delete(self):
        assert self.models.where(
            User.id == Post.user_id).delete().execute() == 8
        assert self.models.where(
            User.id == Post.user_id).select().execute().count == 0
        assert Post.count() == 0
        assert User.count() == 0

    def test_delete2(self):
        assert self.models.where(
            User.id == Post.user_id).delete(Post).execute() == 4
        assert User.select().execute().count == 4
        assert Post.count() == 0

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


class TestJoinModel(Test):

    def setUp(self):
        super(TestJoinModel, self).setUp()
        self.create_data(10)

    def test_select(self):
        assert (Post & User).select().execute().count == 10
        assert (Post & User).where(
            User.name == "name2").select().execute().count == 1
        for post, user in (Post & User).select():
            assert post.post_id
            assert user.id
            assert post.user_id == user.id

    def test_delete(self):
        assert (Post & User).delete().execute() == 20
        assert (Post & User).select().execute().count == 0

    def test_delete2(self):
        assert (Post & User).delete(Post).execute() == 10

    def test_update(self):
        assert (Post & User).where(
            User.name <= "name4"
        ).update(User.name == "hello").execute() == 5
        assert (Post & User).where(
            User.name == "hello"
        ).update(Post.name == "good").execute() == 5

    def test_foreignkey_exception(self):
        try:
            User & Post
        except ForeignKeyNotFound:
            pass
        else:
            raise Exception

    def test_findone(self):
        post, user = (Post & User).findone(User.name == "name1")
        assert user._id and post._id
        assert user._id == post.user_id
        assert user.name == "name1"

    def test_findall(self):

        g = (Post & User).findall(User.name.like("name%"))

        i = 0

        for post, user in g:
            i += 1
            assert user.name and post._id
            assert user.id == post.user_id

        assert i == 10

    def test_getone(self):
        post, user = (Post & User).getone()
        assert post.user_id == user.id == 10

    def test_getall(self):
        g = (Post & User).where(User.id <= 5).getall()
        assert len(tuple(g)) == 5
