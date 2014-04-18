# -*- coding: utf-8 -*-

"""
    CURD.py
    ~~~~~~~

    Tiny Python ORM for MySQL.

    :copyright: (c) 2014 by Chao Wang (Hit9).
    :license: BSD.
"""


__version__ = '0.5.0'


import types
from datetime import date, datetime, time, timedelta

import MySQLdb
from _mysql import escape_dict, escape_sequence, NULL, string_literal


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

QUERY_INSERT = 20
QUERY_UPDATE = 21
QUERY_SELECT = 22
QUERY_DELETE = 23


DATA_ENCODING = 'utf8'


class CURDException(Exception):
    pass


class UnSupportedType(CURDException):
    pass


class ForeignKeyNotFound(CURDException):
    pass


class PrimaryKeyValueNotFound(CURDException):
    pass


class Database(object):

    configs = {
        'host': 'localhost',
        'port': 3306,
        'db': '',
        'user': '',
        'passwd': '',
        'charset': 'utf8'
    }

    autocommit = True

    conn = None

    @classmethod
    def config(cls, autocommit=True, **configs):
        cls.configs.update(configs)
        cls.autocommit = autocommit

        # close active connection on configs change
        if cls.conn and cls.conn.open:
            cls.conn.close()

    @classmethod
    def connect(cls):
        cls.conn = MySQLdb.connect(**cls.configs)
        cls.conn.autocommit(cls.autocommit)

    @classmethod
    def get_conn(cls):
        if not cls.conn or not cls.conn.open:
            cls.connect()

        try:
            cls.conn.ping()  # make sure current connection is working
        except MySQLdb.OperationalError:
            cls.connect()  # connection lost, reconnet

        return cls.conn

    @classmethod
    def execute(cls, sql):
        cursor = cls.get_conn().cursor()
        cursor.execute(sql)
        return cursor

    @classmethod
    def change(cls, db):
        cls.configs['db'] = db

        if cls.conn and cls.conn.open:
            cls.conn.select_db(db)

    select_db = change
