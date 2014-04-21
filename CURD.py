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

    def __repr__(self):
        return '<%s %r>' % (type(self).__name__, Compiler.tostr(self))

    def clone(self, *args, **kwargs):
        obj = type(self)(*args, **kwargs)

        for key, value in self.__dict__.iteritems():
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


class Field(Leaf):

    def __init__(self, is_primarykey=False, is_foreignkey=False):
        self.is_primarykey = is_primarykey
        self.is_foreignkey = is_foreignkey

    def describe(self, name, model):
        self.name = name
        self.model = model
        self.fullname = '%s.%s' % (self.model.table_name, self.name)
        setattr(model, name, FieldDescriptor(self))

    def like(self, pattern):
        return Expr(self, pattern, OP_LIKE)

    def between(self, left, right):
        return Expr(self, (left, right), OP_BETWEEN)

    def _in(self, *values):
        return Expr(self, values, OP_IN)

    def not_in(self, *values):
        return Expr(self, values, OP_NOT_IN)

    def alias(self, _alias):
        field = self.clone()
        field.name = _alias
        field.fullname = '%s as %s' % (self.fullname, _alias)
        setattr(self.model, field.name, FieldDescriptor(self))
        return field


class PrimaryKey(Field):

    def __init__(self):
        super(PrimaryKey, self).__init__(is_primarykey=True)


class ForeignKey(Field):

    def __init__(self, point_to):
        super(ForeignKey, self).__init__(is_foreignkey=True)
        self.point_to = point_to


class Function(Leaf):

    def __init__(self, name, *args):
        self.name = name
        self.args = args
        self.fullname = '%s(%s)' % (
            self.name, ', '.join(map(Compiler.tostr, self.args)))

    def alias(self, _alias):
        fn = self.clone(self.name, *self.args)
        fn.name = _alias
        fn.fullname = '%s as %s' % (self.fullname, _alias)
        return fn


class Fn(object):

    def _e(self, name):
        def e(*args):
            return Function(name, *args)
        return e

    def __getattr__(self, name):
        return self._e(name)


fn = Fn()


class Query(object):

    def __init__(self, type, runtime, target=None):
        self.type = type
        self.sql = Compiler.compile(runtime, self.type, target)
        runtime.reset_data()

    def __repr__(self):
        return '<%s %r>' % (type(self).__name__, self.sql)


class InsertQuery(Query):

    def __init__(self, runtime, target=None):
        super(InsertQuery, self).__init__(QUERY_INSERT, runtime, target)

    def execute(self):
        cursor = Database.execute(self.sql)
        return cursor.lastrowid if cursor.rowcount else None


class UpdateQuery(Query):

    def __init__(self, runtime, target=None):
        super(UpdateQuery, self).__init__(QUERY_UPDATE, runtime, target)

    def execute(self):
        cursor = Database.execute(self.sql)
        return cursor.rowcount


class SelectQuery(Query):

    def __init__(self, runtime, target=None):
        self.from_model = runtime.model
        self.selects = runtime.data['select']
        super(SelectQuery, self).__init__(QUERY_SELECT, runtime, target)

    def __iter__(self):
        results = self.execute()
        return results.fetchall()

    def execute(self):
        cursor = Database.execute(self.sql)
        return None  # TODO


class DeleteQuery(Query):

    def __init__(self, runtime, target=None):
        super(DeleteQuery, self).__init__(QUERY_DELETE, runtime, target)

    def execute(self):
        cursor = Database.execute(self.sql)
        return cursor.rowcount


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
        QUERY_INSERT: 'insert into {target} {set}',
        QUERY_UPDATE: 'update {target} {set} {where}',
        QUERY_SELECT: 'select {select} from {from} {where} {groupby}'
                      ' {having} {orderby} {limit}',
        QUERY_DELETE: 'delete {target} from {from} {where}'
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
        return string_literal('%d %d:%d:%d' % (
            data.days, hours, minutes, seconds))

    def node2str(node):
        return node.fullname

    def expr2str(expr):
        return Compiler.parse_expr(expr)

    def query2str(query):
        return '(%s)' % query.sql

    conversions = {
        datetime: datetime2str,
        date: date2str,
        Field: node2str,
        PrimaryKey: node2str,
        ForeignKey: node2str,
        Function: node2str,
        Expr: expr2str,
        Query: query2str,
        InsertQuery: query2str,
        UpdateQuery: query2str,
        SelectQuery: query2str,
        DeleteQuery: query2str,
        time: time2str,
        timedelta: timedelta2str,
        types.IntType: thing2str,
        types.LongType: thing2str,
        types.FloatType: float2str,
        types.StringType: thing2str,
        types.UnicodeType: unicode2str,
        types.BooleanType: bool2str,
        types.NoneType: None2Null,
        types.TupleType: escape_sequence,
        types.ListType: escape_sequence,
        types.DictType: escape_dict
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

        if expr.op in (
            OP_LT, OP_LE, OP_GT, OP_GE, OP_EQ, OP_NE,
            OP_ADD, OP_AND, OP_OR,  OP_LIKE
        ):
            right = tostr(expr.right)
        elif expr.op is OP_BETWEEN:
            right = '%s and %s' % tuple(map(tostr, expr.right))
        elif expr.op in (OP_IN, OP_NOT_IN):
            right = '(%s)' % ', '.join(map(tostr, expr.right))

        string = '%s %s %s' % (left, mappings[expr.op], right)

        if expr.op in (OP_AND, OP_OR):
            string = '(%s)' % string

        return string

    def _compile(pattern):
        def _e(func):
            def e(lst):
                if not lst:
                    return ''
                return pattern.format(*func(lst))
            return e
        return _e

    @_compile('order by {0}{1}')
    def _orderby(lst):
        node, desc = lst
        return node.fullname, ' desc' if desc else ''

    @_compile('group by {0}')
    def _groupby(lst):
        return ', '.join(f.fullname for f in lst),

    @_compile('having {0}')
    def _having(lst):
        return ' and '.join(map(Compiler.parse_expr, lst)),

    @_compile('where {0}')
    def _where(lst):
        return ' and '.join(map(Compiler.parse_expr, lst)),

    @_compile('{0}')
    def _select(lst):
        return ', '.join(f.fullname for f in lst),

    @_compile('limit {0}{1}')
    def _limit(lst):
        offset, rows = lst
        return '%s, ' % offset if offset else '', rows

    @_compile('set {0}')
    def _set(lst):
        return ', '.join(map(Compiler.parse_expr, lst)),

    compilers = {
        'orderby': _orderby,
        'groupby': _groupby,
        'having': _having,
        'where': _where,
        'select': _select,
        'limit': _limit,
        'set': _set
    }

    @staticmethod
    def compile(runtime, type, target=None):

        if target is None:
            target = runtime.model

        args = {
            'target': target.table_name,
            'from': runtime.model.table_name
        }

        for key, func in Compiler.compilers.items():
            args[key] = func(runtime.data[key])

        pattern = Compiler.patterns[type]

        return pattern.format(**args)


class Runtime(object):

    def __init__(self, model=None):
        self.model = model
        self.reset_data()

    def reset_data(self):
        keys = (
            'where', 'set', 'orderby', 'select', 'limit', 'groupby', 'having')
        self.data = {}.fromkeys(keys, [])

    def __repr__(self):
        return '<Runtime %r>' % self.data

    def set_orderby(self, lst):
        self.data['orderby'] = list(lst)

    def set_groupby(self, lst):
        self.data['groupby'] = list(lst)

    def set_having(self, lst):
        self.data['having'] = list(lst)

    def set_limit(self, lst):
        self.data['limit'] = list(lst)

    def set_select(self, lst):
        self.data['select'] = list(lst) or self.model.get_fields()

    def set_where(self, lst, dct):
        lst = list(lst)

        if self.model.single:
            lst.extend(self.model.fields[k] == v for k, v in dct.iteritems())

        self.data['where'] = lst

    def set_set(self, lst, dct):
        lst = list(lst)

        if self.model.single:
            lst.extend(self.model.fields[k] == v for k, v in dct.iteritems())

        self.data['set'] = lst


class MetaModel(type):

    def __init__(cls, name, bases, attrs):
        table_name = None
        primarykey = None
        fields = {}

        for name, value in cls.__dict__.iteritems():
            if isinstance(value, Field):
                fields[name] = value
                if value.is_primarykey:
                    primarykey = value
            elif name == 'table_name':
                table_name = value

        if table_name is None:
            # default: 'User' => 'user', 'CuteCat' => 'cute_cat'
            table_name = reduce(
                lambda x, y: ('_' if y.isupper() else '').join((x, y)),
                list(cls.__name__)
            ).lower()

        if primarykey is None:
            fields['id'] = primarykey = PrimaryKey()

        cls.primarykey = primarykey
        cls.table_name = table_name
        cls.fields = fields

        for name, field in cls.fields.iteritems():
            field.describe(name, cls)

        cls.runtime = Runtime(cls)


class Model(object):

    __metaclass__ = MetaModel

    single = True

    def __init__(self, *lst, **dct):
        self.data = {}

        for expr in lst:
            field, value = expr.left, expr.right
            self.data[field.name] = value

        self.data.update(dct)
        self._cache = self.data.copy()
        self.set_in_db(False)

    def set_in_db(self, boolean):
        self._in_db = boolean

    @classmethod
    def get_fields(cls):
        return cls.fields.values()

    @classmethod
    def insert(cls, *lst, **dct):
        cls.runtime.set_set(lst, dct)
        return InsertQuery(cls.runtime)

    @classmethod
    def select(cls, *lst):
        cls.runtime.set_select(lst)
        return SelectQuery(cls.runtime)

    @classmethod
    def update(cls, *lst, **dct):
        cls.runtime.set_set(lst, dct)
        return UpdateQuery(cls.runtime)

    @classmethod
    def create(cls, *lst, **dct):
        query = cls.insert(*lst, **dct)
        id = query.execute()

        if id is not None:
            dct[cls.primarykey.name] = id
            instance = cls(*lst, **dct)
            instance.set_in_db(True)
            return instance
        return None

    @classmethod
    def delete(cls):
        return DeleteQuery(cls.runtime)

    @classmethod
    def where(cls, *lst, **dct):
        cls.runtime.set_where(lst, dct)
        return cls

    @classmethod
    def at(cls, id):
        return cls.where(cls.primarykey == id)

    @classmethod
    def orderby(cls, field, desc=False):
        cls.runtime.set_orderby((field, desc))
        return cls

    @classmethod
    def groupby(cls, *lst):
        cls.runtime.set_groupby(lst)
        return cls

    @classmethod
    def limit(cls, rows, offset=None):
        cls.runtime.set_limit((offset, rows))
        return cls
