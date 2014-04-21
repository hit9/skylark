# -*- coding: utf-8 -*-

"""
    CURD.py
    ~~~~~~

    Tiny Python ORM for MySQL.

    :copyright: (c) 2014 by Chao Wang (Hit9).
    :license: BSD.
"""


import types
from datetime import date, datetime, time, timedelta

import MySQLdb
from _mysql import escape_dict, escape_sequence, NULL, string_literal


__version__ = '0.5.0'


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


QUERY_INSERT = 21
QUERY_UPDATE = 22
QUERY_SELECT = 23
QUERY_DELETE = 24


class CURDException(Exception):
    pass


class UnSupportedType(CURDException):
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

        # make sure current connection is working
        try:
            cls.conn.ping()
        except MySQLdb.OperationalError:
            cls.connect()

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

    select_db = change  # alias


class Node(object):
    pass


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

    def __repr__(self):
        return '<%s %r>' % (type(self).__name__, Compiler.tostr(self))


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
        instance.data[self.name] = value


class Field(Node, Leaf):

    def __init__(self, is_primarykey=False, is_foreignkey=False):
        self.is_primarykey = is_primarykey
        self.is_foreignkey = is_foreignkey

    def describe(self, name, model):
        self.name = name
        self.model = model
        self.fullname = '%s.%s' % (self.model.table_name, self.name)
        setattr(model, name, FieldDescriptor(self))

    def like(self, pattern):
        return Expr(self, pattern, OP_BETWEEN)

    def between(self, left, right):
        return Expr(self, (left, right), OP_BETWEEN)

    def _in(self, *values):
        return Expr(self, values, OP_IN)

    def not_in(self, *values):
        return Expr(self, values, OP_NOT_IN)


class PrimaryKey(Field):

    def __init__(self):
        super(PrimaryKey, self).__init__(is_primarykey=True)


class ForeignKey(Field):

    def __init__(self, point_to):
        super(ForeignKey, self).__init__(is_foreignkey=True)
        self.point_to = point_to


class Function(Node, Leaf):

    def __init__(self, name, *args):
        self.name = name
        self.args = args
        self.fullname = '%s(%s)' % (
            self.name, ', '.join(map(Compiler.tostr, self.args)))


class Fn(object):

    def _e(self, name):
        def e(*args):
            return Function(name, *args)
        return e

    def __getattr__(self, name):
        return self._e(name)


fn = Fn()


class Query(object):
    pass


class Compiler(object):

    mappings = {
        OP_LT: '<',
        OP_LE: '<=',
        OP_GT: '>',
        OP_GE: '>=',
        OP_EQ: '=',
        OP_NE: '<>',
        OP_ADD: '+',
        OP_AND: 'and',
        OP_OR: 'or',
        OP_LIKE: 'like',
        OP_BETWEEN: 'between',
        OP_IN: 'in',
        OP_NOT_IN: 'not in'
    }

    patterns = {
        QUERY_INSERT: 'insert into {target}{set}',
        QUERY_UPDATE: 'update {target}{set}{where}',
        QUERY_SELECT: ('select {select} from {from}{where}{groupby}'
                       '{having}{orderby}{limit}'),
        QUERY_DELETE: 'delete {target} from {from}{where}'
    }

    encoding = 'utf8'

    def thing2str(data):
        return string_literal(data)

    def float2str(data):
        return '%.15g' % data

    def None2Null(data):
        return NULL

    def bool2str(data):
        return str(int(data))

    def unicode2str(data):
        return string_literal(data.encode(Compiler.encoding))

    def datetime2str(data):
        return string_literal(data.strftime('%Y-%m-%d %H:%M:%S'))

    def date2str(data):
        return string_literal(data.strftime('%Y-%m-%d'))

    def time2str(data):
        return string_literal(data.strftime('%H:%M:%S'))

    def timedelta2str(data):
        seconds = int(data.seconds) % 60
        minutes = int(data.seconds / 60) % 60
        hours = int(data.seconds / 3600) % 24
        return string_literal('%d %d:%d:%d' % (data.days, hours, minutes,
                                               seconds))

    def node2str(node):
        return node.fullname

    def expr2str(expr):
        return Compiler.parse_expr(expr)

    def query2str(query):
        return '(%s)' % query.sql

    conversions = {
        types.IntType: thing2str,
        types.LongType: thing2str,
        types.FloatType: float2str,
        types.StringType: thing2str,
        types.UnicodeType: unicode2str,
        types.BooleanType: bool2str,
        types.NoneType: None2Null,
        types.TupleType: escape_sequence,
        types.ListType: escape_sequence,
        types.DictType: escape_dict,
        datetime: datetime2str,
        date: date2str,
        time: time2str,
        timedelta: timedelta2str,
        Field: node2str,
        Function: node2str,
        Expr: expr2str,
        Query: query2str
    }

    @staticmethod
    def tostr(e):
        tp = type(e)

        if tp in Compiler.conversions:
            return Compiler.conversions[tp](e)
        raise UnSupportedType

    @staticmethod
    def parse_expr(expr):
        tostr = Compiler.tostr
        mappings = Compiler.mappings

        left = tostr(expr.left)

        if expr.op in (OP_LT, OP_LE, OP_GT, OP_GE, OP_EQ, OP_NE, OP_ADD,
                       OP_AND, OP_OR, OP_LIKE):
            right = tostr(expr.right)
        elif expr.op is OP_BETWEEN:
            right = '%s and %s' % tuple(map(tostr, expr.right))
        elif expr.op in (OP_IN, OP_NOT_IN):
            right = ', '.join(map(tostr, expr.right))

        string = '%s %s %s' % (left, mappings[expr.op], right)

        if expr.op in (OP_AND, OP_OR):
            string = '(%s)' % string

        return string
