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

    Micro python orm for mysql, sqlite and postgres.

    :author: Chao Wang (Hit9).
    :license: BSD.
"""


__version__ = '0.7.5'


import sys


if sys.hexversion < 0x03000000:
    PY_VERSION = 2
else:
    PY_VERSION = 3


# common operators (~100)
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
# special operators (100+)
OP_BETWEEN = 101
OP_IN = 102
OP_NOT_IN = 103


class SkylarkException(Exception):
    pass


class UnSupportedDBAPI(SkylarkException):
    pass


class DBAPI(object):

    placeholder = '%s'

    def __init__(self, module):
        self.module = module

    def conn_is_open(self, conn):
        return conn and conn.open

    def close_conn(self, conn):
        return conn.close()

    def connect(self, configs):
        return self.module.connect(**configs)

    def set_autocommit(self, conn, boolean):
        return conn.autocommit(boolean)

    def setdefault_autocommit(self, conn, configs):
        return conn.autocommit(configs.get('autocommit', True))

    def conn_is_alive(self, conn):
        try:
            conn.ping()
        except self.module.OperationalError:
            return False
        return True  # ok

    def get_cursor(self, conn):
        return conn.cursor()

    def execute_cursor(self, cursor, args):
        return cursor.execute(*args)

    def select_db(self, db, conn, configs):
        configs.update({'db': db})
        if self.conn_is_open(conn):
            conn.select_db(db)

    def begin_transaction(self, conn):
        pass

    def commit_transaction(self, conn):
        return conn.commit()

    def rollback_transaction(self, conn):
        return conn.rollback()


class MySQLdbAPI(DBAPI):
    pass


class PyMySQLAPI(DBAPI):

    def conn_is_open(self, conn):
        return conn and conn.socket and conn._rfile


class Sqlite3API(DBAPI):

    placeholder = '?'

    def conn_is_open(self, conn):
        if conn:
            try:
                # return the total number of db rows that have been modified
                conn.total_changes
            except self.module.ProgrammingError:
                return False
            return True
        return False

    def connect(self, configs):
        db = configs['db']
        return self.module.connect(db)

    def setdefault_autocommit(self, conn, configs):
        conn.isolation_level = configs.get('isolation_level', None)

    def set_autocommit(self, conn, boolean):
        if boolean:
            conn.isolation_level = None
        else:
            conn.isolation_level = ''

    def select_db(self, db, conn, configs):
        # for sqlite3, to change database, must create a new connection
        configs.update({'db': db})
        if self.conn_is_open(conn):
            self.close_conn(conn)

    def conn_is_alive(self, conn):
        return 1   # sqlite is serverless


class Psycopg2API(DBAPI):

    def conn_is_open(self, conn):
        return conn and not conn.closed

    def setdefault_autocommit(self, conn, configs):
        conn.autocommit = configs.get('autocommit', True)

    def set_autocommit(self, conn, boolean):
        conn.autocommit = boolean

    def select_db(self, db, conn, configs):
        # for postgres, to change database, must create a new connection
        configs.update({'database': db})
        if self.conn_is_alive(conn):
            self.close_conn(conn)

    def conn_is_alive(self, conn):
        try:
            conn.isolation_level
        except self.module.OperationalError:
            return False
        return True


DBAPI_MAPPINGS = {
    'MySQLdb': MySQLdbAPI,
    'pymysql': PyMySQLAPI,
    'sqlite3': Sqlite3API,
    'psycopg2': Psycopg2API
}


DBAPI_LOAD_ORDER = ('MySQLdb', 'pymysql', 'psycopg2', 'sqlite3')


class DatabaseType(object):

    def __init__(self):
        self.dbapi = None
        self.conn = None
        self.configs = {}

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
            # clear current configs and connection
            if self.dbapi and self.dbapi.conn_is_open(self.conn):
                self.conn.close()
            self.configs = {}
            self.conn = None
            self.dbapi = DBAPI_MAPPINGS[name](module)
        else:
            raise UnSupportedDBAPI

    def config(self, **configs):
        self.configs.update(configs)

        # close active connection on configs change
        if self.dbapi.conn_is_open(self.conn):
            self.dbapi.close_conn(self.conn)

    def connect(self):
        self.conn = self.dbapi.connect(self.configs)
        self.dbapi.setdefault_autocommit(self.conn, self.configs)
        return self.conn

    def get_conn(self):
        if not (
            self.dbapi.conn_is_open(self.conn) and
            self.dbapi.conn_is_alive(self.conn)
        ):
            self.connect()
        return self.conn

    def __del__(self):
        if self.dbapi.conn_is_open(self.conn):
            return self.dbapi.close_conn(self.conn)

    def execute(self, *args):
        cursor = self.dbapi.get_cursor(self.get_conn())
        self.dbapi.execute_cursor(cursor, args)  # should close the cursor?
        return cursor

    def execute_sql(self, sql):  # execute a sql object
        return self.execute(self, sql.literal, sql.params)

    def change(self, db):
        return self.dbapi.select_db(db, self.conn, self.configs)

    def autocommit(self, boolean):
        return self.dbapi.set_autocommit(self.conn, boolean)

    def begin(self):
        return self.dbapi.begin_transaction(self.conn)

    def commit(self):
        return self.dbapi.commit_transaction(self.conn)

    def rollback(self):
        return self.dbapi.rollback_transaction(self.conn)

    def transaction(self):
        return Transaction(self)

    select_db = change  # alias


database = Database = DatabaseType()


class Transaction(object):

    def __init__(self, database):
        self.database = database

    def begin(self):
        return self.database.begin()

    def commit(self):
        return self.database.commit()

    def rollback(self):
        return self.database.rollback()

    def __enter__(self):
        self.begin()
        return self

    def __exit__(self, except_tp, except_val, trace):
        return self.commit()


class SQL(object):

    def __init__(self, literal, *params):
        self.literal = literal
        self.params = params

    @classmethod
    def format(cls, spec, *args):
        literal = spec % tuple(arg.literal for arg in args)
        params = sum([arg.params for arg in args], tuple())
        return cls(literal, *params)

    @classmethod
    def join(cls, sptr, seq):
        literal = sptr.join(sql.literal for sql in seq)
        params = sum([sql.params for sql in seq], tuple())
        return cls(literal, *params)


sql = SQL


class Leaf(object):

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

    def _in(self, *vals):
        return Expr(self, vals, OP_IN)

    def not_in(self, *vals):
        return Expr(self, vals, OP_NOT_IN)


class Expr(Leaf):

    def __init__(self, left, right, op):
        self.left = left
        self.right = right
        self.op = op
