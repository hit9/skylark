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
    'Database', 'database',
]


import sys


if sys.hexversion < 0x03000000:
    PY_VERSION = 2
else:
    PY_VERSION = 3


DB_API_MySQLdb = 1
DB_API_pymysql = 2
DB_API_sqlite3 = 3


class SkylarkException(Exception):
    pass


class UnSupportedDBAPI(SkylarkException):
    pass


class SL(object):

    def __repr__(self):
        return '<%s %r>' % (type(self).__name__, self._repr)


class DBAPI(SL):

    mappings = {
        'MySQLdb': DB_API_MySQLdb,
        'pymysql': DB_API_pymysql,
        'sqlite3': DB_API_sqlite3,
    }

    def __init__(self, module):
        name = module.__name__

        if name in self.mappings:
            self.module = module
            self.type = self.mappings[name]
        else:
            raise UnSupportedDBAPI

        self._repr = name

    def conn_is_up(self, conn):
        if self.type is DB_API_MySQLdb:
            return conn and conn.open
        if self.type is DB_API_pymysql:
            return conn and conn.socket and conn._rfile


class DatabaseType(SL):

    def __init__(self):
        self.configs = {}
        self.autocommit = True
        self.conn = None
        self.db_api = None

        for name in sorted(DBAPI.mappings.keys(),
                           key=lambda k: DBAPI.mappings[k]):
            try:
                module = __import__(name)
            except ImportError:
                continue
            self.set_db_api(module)
            break

        self._repr = self.db_api._repr

    def set_db_api(self, module):
        self.db_api = DBAPI(module)

    def config(self, autocommit=True, **configs):
        self.configs.update(configs)
        self.autocommit = autocommit

        # close active connection on configs change
        if self.db_api.conn_is_up(self.conn):
            self.conn.close()


database = Database = DatabaseType()
