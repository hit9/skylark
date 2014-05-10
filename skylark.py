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


class MySQLdbAPI(DBAPI):

    def __init__(self, module):
        super(MySQLdbAPI, self).__init__(module)

    def conn_is_up(self, conn):
        return conn and conn.open


class PyMySQLAPI(DBAPI):

    def __init__(self, module):
        super(MySQLdbAPI, self).__init__(module)

    def conn_is_up(self, conn):
        return conn and conn.socket and conn._rfile


DBAPI_MAPPINGS = {
    'MySQLdb': MySQLdbAPI,
    'pymysql': PyMySQLAPI
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


database = Database = DatabaseType()
