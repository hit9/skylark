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
    'database', 'Database'
]


import sys


if sys.hexversion < 0x03000000:
    PY_VERSION = 2
else:
    PY_VERSION = 3


class SkylarkException(Exception):
    pass


class UnSupportedDBAPI(SkylarkException):
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


class MySQLdbAPI(DBAPI):

    def __init__(self, module):
        super(MySQLdbAPI, self).__init__(module)


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

    def execute(self, sql, params=None):
        pass


database = Database = DatabaseType()
