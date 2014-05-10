# -*- coding: utf-8 -*-
#
#            /)
#           / )
#    (\    /  )
#    ( \  /   )
#     ( \/ / )
#     (@)   )
#     / \_   \
#        // \\\
#        ((   \\
#       ~ ~ ~   \
#      skylark
#

"""
    skylark
    ~~~~~~~

    A nice micro orm for python, mysql only.

    :author: Chao Wang (Hit9).
    :license: BSD.
"""

__version__ = '0.7.5'


__all__ = [
    'SkylarkException',
    'UnSupportedDBAPI',
    'DatabaseNotSupportFeature',
    'database', 'Database',
    'sql', 'SQL'
]


import sys


if sys.hexversion < 0x03000000:
    PY_VERSION = 2
else:
    PY_VERSION = 3


OP_LT = 1
OP_LE = 2
OP_GT = 3
OP_GE = 4
OP_EQ = 5
OP_NE = 6
OP_ADD = 7
OP_AND = 8
OP_OR = 9
OP_LIKE = 10
OP_BETWEEN = 11
OP_IN = 12
OP_NOT_IN = 13


class SkylarkException(Exception):
    pass


class UnSupportedDBAPI(SkylarkException):
    pass


class DatabaseNotSupportFeature(SkylarkException):
    pass


class DBAPI(object):

    def __init__(self, module):
        self.module = module

    def conn_is_up(self, conn):
        return conn and conn.open

    def close_conn(self, conn):
        return conn.close()

    def connect(self, **configs):
        return self.module.connect(**configs)

    def set_autocommit(self, autocommit, conn):
        return conn.autocommit(autocommit)

    def ping_conn(self, conn):
        try:
            conn.ping()
        except self.module.OperationalError:
            return False
        return True

    def get_cursor(self, conn):
        return conn.cursor()

    def execute_cursor(self, cursor):
        return cursor.execute()

    def close_cursor(self, cursor):
        return cursor.close()

    def select_db(self, conn, db):
        return conn.select_db(db)


class MySQLdbAPI(DBAPI):

    def __init__(self, module):
        super(MySQLdbAPI, self).__init__(module)

    def __patch_mysqldb_cursor(self, cursor):
        # let MySQLdb.cursor enable fetching after close
        rows = tuple(cursor.fetchall())

        def create_generator():
            for row in rows:
                yield row

        generator = create_generator()

        def fetchall():
            return generator

        def fetchone():
            try:
                return generator.next()
            except StopIteration:
                pass

        cursor.fetchall = fetchall
        cursor.fetchone = fetchone
        return cursor

    def close_cursor(self, cursor):
        cursor = self.__patch_mysqldb_cursor(cursor)
        return super(MySQLdbAPI, self).close_cursor()


class PyMySQLAPI(DBAPI):

    def __init__(self, module):
        super(MySQLdbAPI, self).__init__(module)

    def conn_is_up(self, conn):
        return conn and conn.socket and conn._rfile


class Sqlite3API(DBAPI):

    def __init__(self, module):
        super(Sqlite3API, self).__init__(module)

    def conn_is_up(self, conn):
        pass

    def close_conn(self, conn):
        return conn.close()

    def connect(self, **configs):
        db = configs['db']
        return self.module.connect(db)

    def set_autocommit(self, autocommit, conn):
        conn.isolation_level = None

    def ping_conn(self):
        pass  # TODO

    def select_db(self, conn, db):
        raise DatabaseNotSupportFeature


DBAPI_MAPPINGS = {
    'MySQLdb': MySQLdbAPI,
    'pymysql': PyMySQLAPI,
    'sqlite3': Sqlite3API
}


DBAPI_LOAD_ORDER = ('MySQLdb', 'pymysql', 'sqlite3')


class DatabaseType(object):

    def __init__(self):
        self.configs = {}
        self.autocommit = True
        self.conn = None
        self.dbapi = None

        for name in DBAPI_LOAD_ORDER:
            try:
                module = __import__(name)
            except ImportError:
                continue
            self.set_dbapi(module)
            break

    def set_dbapi(self, module):
        name = module.__name__

        if name in DBAPI_MAPPINGS:
            self.dbapi = DBAPI_MAPPINGS[name](module)
        else:
            raise UnSupportedDBAPI

    def config(self, autocommit=True, **configs):
        self.configs.update(configs)
        self.autocommit = autocommit

        # close active connection on configs change
        if self.dbapi.conn_is_up(self.conn):
            self.dbapi.close_conn(self.conn)

    def connect(self):
        self.conn = self.dbapi.connect(**self.configs)
        self.dbapi.set_autocommit(self.autocommit, self.conn)

    def get_conn(self):
        if not self.dbapi.conn_is_up(self.conn):
            self.connect()

        # make sure current connection is working
        if not self.dbapi.ping_conn(self.conn):
            self.connect()

        return self.conn

    def __del__(self):
        if self.dbapi.conn_is_up(self.conn):
            return self.dbapi.close_conn(self.conn)

    def execute(self, **args):  # args: sql(string), params(tuple/dict)
        cursor = self.dbapi.get_cursor(self.get_conn())
        self.dbapi.execute_cursor(cursor)
        self.dbapi.close_cursor(cursor)
        return cursor

    def execute_sql(self, sql):  # execute a sql object
        if sql.params:
            return self.execute(sql.literal, sql.params)
        return self.execute(sql.literal)

    def change(self, db):
        self.configs.update({'db': db})

        if self.dbapi.conn_is_up(self.conn):
            return self.dbapi.select_db(self.conn, db)

    select_db = change  # alias


database = Database = DatabaseType()


class SQL(object):

    def __init__(self, literal, params=None):
        self.literal = literal
        if params is None:
            params = tuple()
        self.params = params


sql = SQL  # alias


class Node(object):

    def clone(self, *args, **kwargs):
        obj = type(self)(*args, **kwargs)
        for key, value in self.__dict__.items():
            setattr(obj, key, value)
        return obj


class Leaf(Node):

    def _e(op):
        def e(self, right):
            return Expr(self, right, op)
        return e

    __lt__ = _e(OP_LT)

    __le__ = _e(OP_LE)

    __gt__ = _e(OP_GT)

    __ge__ = _e(OP_GE)

    __eq__ = _e(OP_EQ)

    __ne__ = _e(OP_NE)

    __add__ = _e(OP_ADD)

    __and__ = _e(OP_AND)

    __or__ = _e(OP_OR)

    def like(self, pattern):
        return Expr(self, pattern, OP_LIKE)

    def between(self, left, right):
        return Expr(self, (left, right), OP_BETWEEN)

    def _in(self, *values):
        return Expr(self, values, OP_IN)

    def not_in(self, *values):
        return Expr(self, values, OP_NOT_IN)


class Expr(Leaf):

    def __init__(self, left, right, op):
        self.left = left
        self.right = right
        self.op = op


class FieldDescriptor(object):

    def __init__(self, field):
        self.field = field

    def __get__(self, instance, type=None):
        if instance:
            return instance.data[self.field.name]
        return self.field

    def __set__(self, instance, value):
        instance.data[self.field.name] = value


class Field(Leaf):

    def __init__(self, is_primarykey=False, is_foreignkey=False):
        self.is_primarykey = is_primarykey
        self.is_foreignkey = is_foreignkey

    def describe(self, name, model):
        self.name = name
        self.model = model
        self.fullname = '%s.%s' % (self.model.table_name, self.name)
        setattr(model, name, FieldDescriptor(self))

    def alias(self, _alias):
        field = self.clone()
        field.name = _alias
        field.fullname = '%s as %s' % (self.fullname, _alias)
        setattr(self.model, field.name, FieldDescriptor(field))
        return field


class PrimaryKey(Field):

    def __init__(self):
        super(PrimaryKey, self).__init__(is_primarykey=True)


class ForeignKey(Field):

    def __init__(self, point_to):
        super(ForeignKey, self).__init__(is_foreignkey=True)
        self.point_to = point_to
