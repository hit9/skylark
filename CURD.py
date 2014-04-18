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
        self.is_primarykey = is_primarykey
        self.is_foreignkey = is_foreignkey

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

        cache = Compiler.expr_cache

        if expr in cache:
            return cache[expr]

        l, op, r = expr.left, expr.op, expr.right
        OP_MAPPING = Compiler.OP_MAPPING
        tostr = Compiler.__parse_expr_one_side

        string = None

        if op in OP_MAPPING:
            string = tostr(l) + OP_MAPPING[op] + tostr(r)
        elif op is OP_BETWEEN:
            string = '%s between %s and %s' % (tostr(l), tostr(r[0]),
                                               tostr(r[1]))
        elif op in (OP_IN, OP_NOT_IN):
            string = '%s%s in (%s)' % (
                tostr(l),
                ' not' if op is OP_NOT_IN else '',
                ', '.join(tostr(value) for value in r)
            )

        if op in (OP_AND, OP_OR):
            string = '(%s)' % string

        cache[expr] = string

        return string

    @staticmethod
    def parse_orderby(lst):
        if not lst:
            return ''
        field, desc = lst
        return ' order by %s%s' % (field.fullname, ' desc' if desc else '')

    @staticmethod
    def parse_groupby(lst):
        if not lst:
            return ''
        return ' group by %s' % (', '.join(f.fullname for f in lst))

    @staticmethod
    def parse_having(lst):
        if not lst:
            return ''
        return ' having %s' % (' and '.join(
            Compiler.parse_expr(expr) for expr in lst))

    @staticmethod
    def parse_where(lst):
        if not lst:
            return ''
        return ' where %s' % (' and '.join(
            Compiler.parse_expr(expr) for expr in lst))

    @staticmethod
    def parse_select(lst):
        return ', '.join(f.fullname for f in lst)

    @staticmethod
    def parse_limit(lst):
        if not lst:
            return ''
        offset, rows = lst
        return ' limit %s%s' % ('%s, ' % offset if offset else '', rows)

    @staticmethod
    def parse_set(lst):
        return ' set %s' % (', '.join(
            Compiler.parse_expr(expr) for expr in lst))

    @staticmethod
    def parse_distinct(boolean):
        return ' distinct' if boolean else ''

    @staticmethod
    def gen_sql(runtime, query_type, target_model=None):
        from_table = runtime.model.table_name

        if target_model is None:
            target_model = runtime.model

        target_table = target_model.table_name

        _where = Compiler.parse_where(runtime.data['where'])
        _set = Compiler.parse_set(runtime.data['set'])
        _orderby = Compiler.parse_orderby(runtime.data['orderby'])
        _select = Compiler.parse_select(runtime.data['select'])
        _limit = Compiler.parse_limit(runtime.data['limit'])
        _groupby = Compiler.parse_groupby(runtime.data['groupby'])
        _having = Compiler.parse_having(runtime.data['having'])
        _distinct = Compiler.parse_distinct(runtime.data['distinct'])

        pattern = Compiler.SQL_PATTERNS[query_type]

        return pattern.format(**{
            'target': target_table,
            'set': _set,
            'from': from_table,
            'where': _where,
            'select': _select,
            'limit': _limit,
            'orderby': _orderby,
            'groupby': _groupby,
            'having': _having,
            'distinct': _distinct,
        })


class Runtime(object):

    def __init__(self, model=None):
        self.model = model
        self.data = {}.fromkeys(('where', 'set', 'orderby', 'select', 'limit',
                                 'groupby', 'having', 'distinct'), None)
        self.reset_data()

    def reset_data(self):
        dct = dict((key, []) for key in self.data.keys())
        dct['distinct'] = False
        self.data.update(dct)

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

    def set_select(self, flst):
        self.data['select'] = list(flst) or self.model.get_fields()

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

    def set_distinct(self, boolean):
        self.data['distinct'] = boolean


class Query(object):

    def __init__(self, query_type, runtime, target_model=None):
        self.query_type = query_type
        self.sql = Compiler.gen_sql(runtime, self.query_type, target_model)
        runtime.reset_data()  # ! clean runtime right on query initialized

    def __repr__(self):
        return '<%s %r>' % (type(self).__name__, self.sql)


class InsertQuery(Query):

    def __init__(self, runtime, target_model=None):
        super(InsertQuery, self).__init__(QUERY_INSERT, runtime, target_model)

    def execute(self):
        cursor = Database.execute(self.sql)
        return cursor.lastrowid if cursor.rowcount else None


class UpdateQuery(Query):

    def __init__(self, runtime, target_model=None):
        super(UpdateQuery, self).__init__(QUERY_UPDATE, runtime, target_model)

    def execute(self):
        cursor = Database.execute(self.sql)
        return cursor.rowcount


class SelectQuery(Query):

    def __init__(self, runtime, target_model=None):
        self.from_model = runtime.model
        self.selects = runtime.data['select']
        super(SelectQuery, self).__init__(QUERY_SELECT, runtime, target_model)

    def __iter__(self):
        result = self.execute()
        return result.fetchall()

    def execute(self):
        cursor = Database.execute(self.sql)
        return SelectResult(cursor, self.from_model, self.selects)


class DeleteQuery(Query):

    def __init__(self, runtime, target_model=None):
        super(DeleteQuery, self).__init__(QUERY_DELETE, runtime, target_model)

    def execute(self):
        cursor = Database.execute(self.sql)
        return cursor.rowcount


class SelectResult(object):

    def __init__(self, cursor, model, flst):
        self.model = model
        self.flst = flst  # fields or functions select
        self.cursor = cursor

    def __instance_from_db(self, model, row):
        instance = model()
        instance.set_in_db(True)

        for idx, f in enumerate(self.flst):
            if f.model is model:
                if isinstance(f, Field):
                    instance.data[f.name] = row[idx]
                elif isinstance(f, Function):
                    setattr(instance, f.name, row[idx])
        return instance

    def fetchone(self):
        row = self.cursor.fetchone()

        if row is None:
            return None

        if self.model.single:
            return self.__instance_from_db(self.model, row)
        else:
            return tuple(
                self.__instance_from_db(m, row) for m in self.model.models)

    def fetchall(self):
        rows = self.cursor.fetchall()

        if self.model.single:
            for row in rows:
                yield self.__instance_from_db(self.model, row)
        else:
            for row in rows:
                yield tuple(
                    self.__instance_from_db(m, row) for m in self.model.models)

    @property
    def count(self):
        return self.cursor.rowcount


class MetaModel(type):

    def __init__(cls, name, bases, attrs):

        table_name = None
        primarykey = None
        fields = {}  # {field_name: field}

        for name, value in cls.__dict__.iteritems():
            if isinstance(value, Field):
                fields[name] = value
                if value.is_primarykey:
                    primarykey = value
            elif name == 'table_name':
                table_name = value

        if table_name is None:
            # default table_name. User => 'user', 'CuteCat' => 'cute_cat'
            table_name = reduce(lambda x, y: ('_' if y.isupper() else '').join(
                (x, y)), list(cls.__name__)).lower()

        if primarykey is None:
            primarykey = PrimaryKey()   # default: `id`
            fields['id'] = primarykey

        cls.primarykey = primarykey
        cls.table_name = table_name
        cls.fields = fields

        for name, field in cls.fields.iteritems():
            field.describe(name, cls)

        cls.runtime = Runtime(cls)

    def __and__(self, join):
        return JoinModel(self, join)

    def __contains__(self, obj):
        if isinstance(obj, self):
            query = self.where(**obj.data).select()
            result = query.execute()
            if result.count:
                return True
        return False


class Model(object):

    __metaclass__ = MetaModel

    single = True  # single model

    def __init__(self, *lst, **dct):
        self.data = {}

        for expr in lst:
            field, value = expr.left, expr.right
            self.data[field.name] = value

        self.data.update(dct)
        self._cache = self.data.copy()  # cache for data
        self.set_in_db(False)

    @classmethod
    def get_fields(cls):
        return cls.fields.values()

    @classmethod
    def insert(cls, *lst, **dct):
        cls.runtime.set_set(lst, dct)
        return InsertQuery(cls.runtime)

    @classmethod
    def select(cls, *flst):
        cls.runtime.set_select(flst)
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
            dct[cls.primarykey.name] = id  # add id to dct
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
    def at(cls, _id):
        return cls.where(cls.primarykey == _id)

    @classmethod
    def orderby(cls, field, desc=False):
        cls.runtime.set_orderby((field, desc))
        return cls

    @classmethod
    def groupby(cls, *lst):
        cls.runtime.set_groupby(lst)
        return cls

    @classmethod
    def having(cls, *lst):
        cls.runtime.set_having(lst)
        return cls

    @classmethod
    def limit(cls, rows, offset=None):
        cls.runtime.set_limit((offset, rows))
        return cls

    @classmethod
    def distinct(cls):
        cls.runtime.set_distinct(True)
        return cls

    #  ------------------ {{{select shortcuts

    @classmethod
    def findone(cls, *lst, **dct):
        query = cls.where(*lst, **dct).select()
        result = query.execute()
        return result.fetchone()

    @classmethod
    def findall(cls, *lst, **dct):
        query = cls.where(*lst, **dct).select()
        result = query.execute()
        return result.fetchall()

    @classmethod
    def getone(cls):
        return cls.select().execute().fetchone()

    @classmethod
    def getall(cls):
        return cls.select().execute().fetchall()

    # ------------ select shortcuts }}}

    @property
    def _id(self):
        return self.data.get(type(self).primarykey.name, None)

    def set_in_db(self, boolean):
        self._in_db = boolean

    def save(self):
        model = type(self)

        if not self._in_db:  # insert
            id = model.insert(**self.data).execute()

            if id is not None:
                self.data[model.primarykey.name] = id  # set primarykey value
                self.set_in_db(True)
                self._cache = self.data.copy()  # sync cache after saving
            return id
        else:  # update
            # only update changed data
            dct = dict(set(self.data.items()) - set(self._cache.items()))

            # need its primarykey value to track this instance
            if self._id is None:
                raise PrimaryKeyValueNotFound

            if dct:
                query = model.at(self._id).update(**dct)
                rows_affected = query.execute()
            else:
                rows_affected = 0L
            self._cache = self.data.copy()  # sync cache after saving
            return rows_affected

    def destroy(self):
        if self._in_db:
            #! need primarykey to track this instance
            if self._id is None:
                raise PrimaryKeyValueNotFound
            return type(self).at(self._id).delete().execute()
        return None

    def func(func_type):
        @classmethod
        def _func(cls, field=None):
            if field is None:
                field = cls.primarykey
            func = Function(field, func_type)
            query = cls.select(func)
            result = query.execute()
            instance = result.fetchone()
            return getattr(instance, func.name)
        return _func

    count = func(FUNC_COUNT)

    sum = func(FUNC_SUM)

    max = func(FUNC_MAX)

    min = func(FUNC_MIN)

    avg = func(FUNC_AVG)


class Models(object):

    def __init__(self, *models):
        self.models = list(models)
        self.single = False
        self.runtime = Runtime(self)
        self.table_name = ", ".join([m.table_name for m in self.models])
        self.primarykey = [m.primarykey for m in self.models]

    def get_fields(self):
        lst = [m.get_fields() for m in self.models]
        return sum(lst, [])

    def select(self, *lst):
        self.runtime.set_select(lst)
        return SelectQuery(self.runtime)

    def update(self, *lst):
        self.runtime.set_set(lst, {})
        return UpdateQuery(self.runtime)

    def delete(self, target_model=None):
        return DeleteQuery(self.runtime, target_model=target_model)

    def where(self, *lst):
        self.runtime.set_where(lst, {})
        return self

    def orderby(self, field, desc=False):
        self.runtime.set_orderby((field, desc))
        return self

    def groupby(self, *lst):
        self.runtime.set_groupby(lst)
        return self

    def having(self, *lst):
        self.runtime.set_having(lst)
        return self

    def limit(self, rows, offset=None):
        self.runtime.set_limit((offset, rows))
        return self

    def distinct(self):
        self.runtime.set_distinct(True)
        return self

    def findone(self, *lst):
        query = self.where(*lst).select()
        result = query.execute()
        return result.fetchone()

    def findall(self, *lst):
        query = self.where(*lst).select()
        result = query.execute()
        return result.fetchall()

    def getone(self):
        return self.select().execute().fetchone()

    def getall(self):
        return self.select().execute().fetchall()


class JoinModel(Models):

    def __init__(self, main, join):
        super(JoinModel, self).__init__(main, join)

        self.bridge = None

        for field in main.get_fields():
            if field.is_foreignkey and field.point_to is join.primarykey:
                self.bridge = field

        if not self.bridge:
            raise ForeignKeyNotFound(
                "Foreign key references to '%s' not found"
                " in '%s'" % (join.__name__, main.__name__))

    def _brigde(func):
        def e(self, *arg, **kwarg):
            self.runtime.data['where'].append(
                self.bridge == self.bridge.point_to)
            return func(self, *arg, **kwarg)
        return e

    @_brigde
    def select(self, *lst):
        return super(JoinModel, self).select(*lst)

    @_brigde
    def update(self, *lst):
        return super(JoinModel, self).update(*lst)

    @_brigde
    def delete(self, target_model=None):
        return super(JoinModel, self).delete(target_model)
