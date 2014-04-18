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

FUNC_COUNT = 31
FUNC_SUM = 32
FUNC_MAX = 33
FUNC_MIN = 34
FUNC_AVG = 35

FUNC_UCASE = 41
FUNC_LCASE = 42


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

        # make sure current connection is working
        try:
            cls.conn.ping()
        except MySQLdb.OperationalError:
            # connection lost, reconnet
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


class Expr(Leaf):

    def __init__(self, left, right, op):
        self.left = left
        self.right = right
        self.op = op

    def __attrs(self):
        return (self.left, self.op, self.right)

    def __hash__(self):
        return hash(self.__attrs())

    def __eq__(self, other):
        return self.__attrs() == other.__attrs()

    def __repr__(self):
        return '<Expression %r>' % Compiler.parse_expr(self)


class FieldDescriptor(object):

    def __init__(self, field):
        self.name = field.name
        self.field = field

    def __get__(self, instance, type=None):
        if instance:
            return instance.data[self.name]
        return self.field

    def __set__(self, instance, value):
        instance.data[self.name] = value


class Field(Leaf):

    def __init__(self, is_primarykey=False, is_foreignkey=False):
        self.is_primarykey = False
        self.is_foreignkey = False

    def describe(self, name, model):
        self.name = name
        self.model = model
        self.fullname = '%s.%s' % (self.model.table_name, self.name)
        setattr(model, name, FieldDescriptor(self))

    def __repr__(self):
        return '<Field %r>' % self.fullname

    def like(self, pattern):
        return Expr(self, pattern, OP_LIKE)

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


class Function(Leaf):

    mappings = {
        FUNC_COUNT: 'count',
        FUNC_MAX: 'max',
        FUNC_SUM: 'sum',
        FUNC_MIN: 'min',
        FUNC_AVG: 'avg',
        FUNC_UCASE: 'ucase',
        FUNC_LCASE: 'lcase',
    }

    def __init__(self, field, func_type):
        self.field = field
        self.func_type = func_type
        self.fullname = '%s(%s)' % (
            Function.mappings[self.func_type], field.fullname)
        self.name = '%s_of_%s' % (
            Function.mappings[self.func_type], field.name)
        self.model = self.field.model

    def __repr__(self):
        return '<Function %r>' % self.fullname


class Fn(object):

    def func(func_type):
        @classmethod
        def e(cls, field):
            return Function(field, func_type)
        return e

    count = func(FUNC_COUNT)

    sum = func(FUNC_SUM)

    max = func(FUNC_MAX)

    min = func(FUNC_MIN)

    avg = func(FUNC_AVG)

    ucase = func(FUNC_UCASE)

    lcase = func(FUNC_LCASE)


fn = Fn


class Compiler(object):

    OP_MAPPING = {
        OP_LT: ' < ',
        OP_LE: ' <= ',
        OP_GT: ' > ',
        OP_GE: ' >= ',
        OP_EQ: ' = ',
        OP_NE: ' <> ',
        OP_ADD: ' + ',
        OP_AND: ' and ',
        OP_OR: ' or ',
        OP_LIKE: ' like '
    }

    SQL_PATTERNS = {
        QUERY_INSERT: 'insert into {target}{set}',
        QUERY_UPDATE: 'update {target}{set}{where}',
        QUERY_SELECT: ('select{distinct} {select} from {from}{where}{groupby}'
                       '{having}{orderby}{limit}'),
        QUERY_DELETE: 'delete {target} from {from}{where}'
    }

    expr_cache = {}

    def thing2str(data):
        return string_literal(data)

    def float2str(data):
        return '%.15g' % data

    def None2Null(data):
        return NULL

    def bool2str(data):
        return str(int(data))

    def unicode2str(data):
        return string_literal(data.encode(DATA_ENCODING))

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
        return string_literal('%d %d:%d:%d' % (
            data.days, hours, minutes, seconds))

    conversions = {
        types.IntType: thing2str,
        types.LongType: thing2str,
        types.FloatType: float2str,
        types.NoneType: None2Null,
        types.TupleType: escape_sequence,
        types.ListType: escape_sequence,
        types.DictType: escape_dict,
        types.StringType: thing2str,
        types.BooleanType: bool2str,
        types.UnicodeType: unicode2str,
        datetime: datetime2str,
        date: date2str,
        time: time2str,
        timedelta: timedelta2str,
    }

    @staticmethod
    def __parse_expr_one_side(side):

        if isinstance(side, (Field, Function)):
            return side.fullname
        elif isinstance(side, Expr):
            return Compiler.parse_expr(side)
        elif isinstance(side, Query):
            return '(%s)' % side.sql
        elif type(side) in Compiler.conversions:
            return Compiler.conversions[type(side)](side)
        else:
            raise UnSupportedType('Unsupported type: %r' % type(side))

    @staticmethod
    def parse_expr(expr):
        pass
