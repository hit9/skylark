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


__all__ = [
    '__version__',
    'SkylarkException',
    'UnSupportedDBAPI',
    'database', 'Database',
    'sql', 'SQL',
    'Field',
    'PrimaryKey',
    'ForeignKey',
    'fn',
    'Model',
]


__version__ = '0.7.5'


import sys


if sys.hexversion < 0x03000000:
    PY_VERSION = 2
else:
    PY_VERSION = 3


if PY_VERSION == 3:
    from functools import reduce

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

# query types
QUERY_INSERT = 21
QUERY_UPDATE = 22
QUERY_SELECT = 23
QUERY_DELETE = 24


# runtimes
RUNTIME_SET = 1
RUNTIME_VALUES = 2
RUNTIME_SELECT = 3
RUNTIME_WHERE = 4
RUNTIME_GROUPBY = 5
RUNTIME_HAVING = 6
RUNTIME_ORDERBY = 7
RUNTIME_LIMIT = 8


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

    def connect(self, **configs):
        return self.module.connect(**configs)

    def setdefault_autocommit(self, conn, configs):
        return conn.autocommit(configs.get('autocommit', True))

    def get_autocommit(self, conn):
        return bool(conn.autocommit)

    def conn_is_alive(self, conn):
        try:
            conn.ping()
        except self.module.OperationalError:
            return False
        return True  # ok

    def get_cursor(self, conn):
        return conn.cursor()

    def execute_cursor(self, cursor, *args):
        return cursor.execute(*args)

    def close_cursor(self, cursor):
        return cursor.close()

    def select_db(self, db, conn, configs):
        configs.update({'db': db})
        if self.conn_is_open(conn):
            conn.select_db(db)


class MySQLdbAPI(DBAPI):

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
        return super(MySQLdbAPI, self).close_cursor(cursor)


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

    def connect(self, **configs):
        db = configs['db']
        return self.module.connect(db)

    def setdefault_autocommit(self, conn, configs):
        conn.isolation_level = configs.get('isolation_level', None)

    def get_autocommit(self, conn):
        if conn.isolation_level is None:
            return True
        return False

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
            self.configs = {}
            if self.dbapi and self.dbapi.conn_is_open(self.conn):
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
        self.conn = self.dbapi.connect(**self.configs)
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
        self.dbapi.execute_cursor(cursor, *args)
        self.dbapi.close_cursor(cursor)
        return cursor

    def execute_sql(self, sql):  # execute a sql object
        return self.execute(self, sql.literal, sql.params)

    def change(self, db):
        return self.dbapi.select_db(db, self.conn, self.configs)

    select_db = change  # alias


database = Database = DatabaseType()


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
        literal = sptr.join(s.literal for s in seq)
        params = sum([s.params for s in seq], tuple())
        return cls(literal, *params)


sql = SQL  # alias


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

    def _in(self, *values):
        return Expr(self, values, OP_IN)

    def not_in(self, *values):
        return Expr(self, values, OP_NOT_IN)


class Expr(Leaf):

    def __init__(self, left, right, op):
        self.left = left
        self.right = right
        self.op = op


class Alias(object):

    def __init__(self, name, inst):
        for key, value in inst.__dict__.items():
            setattr(self, key, value)
        self.name = name
        self.inst = inst


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
        self.fullname = '%s.%s' % (model.table_name, name)
        setattr(model, name, FieldDescriptor(self))

    def alias(self, alias_name):
        _alias = Alias(alias_name, self)
        setattr(self.model, alias_name, FieldDescriptor(_alias))
        return _alias


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

    def alias(self, alias_name):
        return Alias(alias_name, self)


class Func(object):

    def __init__(self, data=None):
        if data is None:
            data = {}
        self.data = data

    def __getattr__(self, name):
        if name in self.data:
            return self.data[name]
        raise AttributeError

    def __getitem__(self, key):
        return self.data[key]


class Fn(object):

    def _e(self, name):
        def e(*args):
            return Function(name, *args)
        return e

    def __getattr__(self, name):
        return self._e(name)


fn = Fn()


class Distinct(object):
    # 'distinct user.name, user.email..' -> legal
    # 'user.id distinct user.name' -> illegal
    # 'user.id, count(distinct user.name)' -> legal

    def __init__(self, *args):
        self.args = args


distinct = Distinct


class Query(object):

    def __init__(self, type, runtime, target=None):
        self.type = type
        self.sql = compiler.compile(self.type, runtime, target)
        runtime.reset_data()


class InsertQuery(Query):

    def __init__(self, runtime, target=None):
        super(InsertQuery, self).__init__(QUERY_INSERT, runtime, target)

    def execute(self):
        cursor = database.execute_sql(self.sql)
        return cursor.lastrowid if cursor.rowcount else None


class UpdateQuery(Query):

    def __init__(self, runtime, target=None):
        super(UpdateQuery, self).__init__(QUERY_UPDATE, runtime, target)

    def execute(self):
        cursor = database.execute_sql(self.sql)
        return cursor.rowcount


class SelectQuery(Query):

    def __init__(self, runtime):
        self.model = runtime.model
        self.nodes = runtime.data[RUNTIME_SELECT]
        super(SelectQuery, self).__init__(QUERY_SELECT, runtime, None)

    def __iter__(self):
        results = self.execute()
        return results.all()

    def execute(self):
        cursor = database.execute_sql(self.sql)
        return SelectResult(cursor, self.model, self.nodes)


class DeleteQuery(Query):

    def __init__(self, runtime, target=None):
        super(DeleteQuery, self).__init__(QUERY_DELETE, runtime, target)

    def execute(self):
        cursor = database.execute_sql(self.sql)
        return cursor.rowcount


class SelectResult(object):

    def __init__(self, cursor, model, nodes):
        self.cursor = cursor
        self.model = model
        self.count = self.cursor.rowcount

        # distinct should be the first select node if it exists
        if len(nodes) >= 1 and isinstance(nodes[0], Distinct):
            nodes = list(nodes[0].args) + nodes[1:]

        self.fields = {}
        self.funcs = {}

        for idx, node in enumerate(nodes):
            if isinstance(node, Field):
                self.fields[idx] = node
            elif isinstance(node, Function):
                self.funcs[idx] = node

        # returns: 0->inst, 1->func, 2->inst, func
        if self.fields and not self.funcs:
            self.returns = 0
        elif not self.fields and self.funcs:
            self.returns = 1
        elif self.fields and self.funcs:
            self.returns = 2

    def inst(self, model, row):
        inst = model()
        inst.set_in_db(True)

        for idx, field in self.fields.items():
            if field.model is model:
                inst.data[field.name] = row[idx]
        return inst

    def func(self, row):
        func = Func()

        for idx, function in self.funcs.items():
            func.data[function.name] = row[idx]
        return func

    def __one(self, row):
        func = self.func(row)

        if self.model.single:
            inst = self.inst(self.model, row)
            return {0: inst, 1: func, 2: (inst, func)}[self.returns]
        else:
            insts = tuple(map(lambda m: self.inst(m, row), self.model.models))
            return {0: insts, 1: func, 2: insts + (func, )}[self.returns]

    def one(self):
        row = self.cursor.fetchone()

        if row is None:
            return None
        return self.__one(row)

    def all(self):
        rows = self.cursor.fetchall()

        for row in rows:
            yield self.__one(row)

    def tuples(self):
        for row in self.cursor.fetchall():
            yield row

    def dicts(self):
        for row in self.cursor.fetchall():
            dct = {}
            for idx, field in self.fields.items():
                if field.name not in dct:
                    dct[field.name] = row[idx]
                else:
                    dct[field.fullname] = row[idx]
            for idx, func in self.funcs.items():
                dct[func.name] = row[idx]
            yield dct


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

    def query2sql(query):
        spec = '(%s)'
        return sql.format(spec, query.sql)

    def alias2sql(alias):
        spec = '%%s as %s' % alias.name
        return sql.format(spec, compiler.sql(alias.inst))

    def field2sql(field):
        return sql('%s.%s' % (field.model.table_name, field.name))

    def function2sql(function):
        spec = '%s(%%s)' % function.name
        args = sql.join(', ', map(compiler.sql, function.args))
        return sql.format(spec, args)

    def distinct2sql(distinct):
        args = sql.join(', ', map(compiler.sql, distinct.args))
        return sql.format('distinct(%s)', args)

    def expr2sql(expr):
        op = compiler.mappings[expr.op]
        left = compiler.sql(expr.left)

        if expr.op < 100:  # common operators
            right = compiler.sql(expr.right)
        elif expr.op is OP_BETWEEN:
            right = sql.join(' and ', map(compiler.sql, expr.right))
        elif expr.op in (OP_IN, OP_NOT_IN):
            right = sql.format(
                '(%s)', sql.join(', ', map(compiler.sql, expr.right)))

        spec = '%%s %s %%s' % op

        if expr.op in (OP_AND, OP_OR):
            spec = '(%s)' % spec

        return sql.format(spec, left, right)

    conversions = {
        Expr: expr2sql,
        Alias: alias2sql,
        Field: field2sql,
        PrimaryKey: field2sql,
        ForeignKey: field2sql,
        Function: function2sql,
        Distinct: distinct2sql,
        Query: query2sql,
        InsertQuery: query2sql,
        UpdateQuery: query2sql,
        SelectQuery: query2sql,
        DeleteQuery: query2sql
    }

    def sql(self, inst):
        tp = type(inst)
        if tp in self.conversions:
            return self.conversions[tp](inst)
        return sql(database.dbapi.placeholder, inst)

    def orderby2sql(lst):
        node, desc = lst
        spec = 'order by %%s%s' % (' desc' if desc else '')
        return sql.format(spec, node)

    def groupby2sql(lst):
        spec = 'group by %s'
        arg = sql.join(', ', map(compiler.sql, lst))
        return sql.format(spec, arg)

    def having2sql(lst):
        spec = 'having %s'
        arg = sql.join(' and ', map(compiler.sql, lst))
        return sql.format(spec, arg)

    def where2sql(lst):
        spec = 'where %s'
        arg = sql.join(' and ', map(compiler.sql, lst))
        return sql.format(spec, arg)

    def select2sql(lst):
        return sql.join(', ', map(compiler.sql, lst))

    def limit2sql(lst):
        offset, rows = lst
        spec = 'limit %s%s'
        return sql(spec % ('%s, ' % offset if offset else '', rows))

    def set2sql(lst):
        return sql.join(', ', map(compiler.sql, lst))

    def values2sql(lst):
        spec = '(%s) values (%s)'
        keys = [expr.left for expr in lst]
        values = [expr.right for expr in lst]
        keys_sql = sql.join(', ', map(compiler.sql, keys))
        values_sql = sql.join(', ', map(compiler.sql, values))
        return sql.format(spec, keys_sql, values_sql)

    runtime_conversions = {
        RUNTIME_ORDERBY: orderby2sql,
        RUNTIME_GROUPBY: groupby2sql,
        RUNTIME_HAVING: having2sql,
        RUNTIME_WHERE: where2sql,
        RUNTIME_SELECT: select2sql,
        RUNTIME_LIMIT: limit2sql,
        RUNTIME_SET: set2sql,
        RUNTIME_VALUES: values2sql
    }

    query_specs = {
        QUERY_INSERT: 'insert into {target} %s',
        QUERY_UPDATE: 'update {target} %s %s',
        QUERY_SELECT: 'select %s from {from} %s %s %s %s %s',
        QUERY_DELETE: 'delete {target} from {from} %s'
    }

    query_runtimes = {
        QUERY_INSERT: [RUNTIME_VALUES],
        QUERY_UPDATE: [RUNTIME_SET, RUNTIME_WHERE],
        QUERY_SELECT: [RUNTIME_SELECT, RUNTIME_WHERE, RUNTIME_GROUPBY,
                       RUNTIME_HAVING, RUNTIME_ORDERBY, RUNTIME_LIMIT],
        QUERY_DELETE: [RUNTIME_WHERE]
    }

    def compile(self, type, runtime, target=None):
        if target is None:
            target = runtime.model

        spec = self.query_specs[type].format(**{
            'from': runtime.model.table_name,
            'target': target.table_name
        })

        args = []

        for tp in self.query_runtimes[type]:
            data = runtime.data[tp]
            if data:
                args.append(self.runtime_conversions[tp](data))
            else:
                args.append(sql(''))

        return sql.format(spec, *args)


compiler = Compiler()


class Runtime(object):

    RUNTIMES = (
        RUNTIME_WHERE,
        RUNTIME_VALUES,
        RUNTIME_SET,
        RUNTIME_ORDERBY,
        RUNTIME_SELECT,
        RUNTIME_LIMIT,
        RUNTIME_GROUPBY,
        RUNTIME_HAVING
    )

    def __init__(self, model):
        self.model = model
        self.reset_data()

    def reset_data(self):
        # dont use {}.fromkeys(keys, [])
        self.data = dict((key, []) for key in self.RUNTIMES)

    def e(tp):
        def _e(self, lst):
            self.data[tp] = list(lst)
        return _e

    set_orderby = e(RUNTIME_ORDERBY)  # field/function, desc(boolean)

    set_groupby = e(RUNTIME_GROUPBY)  # fields/functions

    set_having = e(RUNTIME_HAVING)  # exprs

    set_limit = e(RUNTIME_LIMIT)  # rows, offset

    set_select = e(RUNTIME_SELECT)  # fields/functions/alias/distincts

    set_set = e(RUNTIME_SET)  # value mappings to update

    set_where = e(RUNTIME_WHERE)  # exprs/mappings

    set_values = e(RUNTIME_VALUES)  # value mappings to insert


class MetaModel(type):

    def __init__(cls, name, bases, attrs):
        table_name = None
        table_prefix = None
        primarykey = None
        fields = {}

        for name, value in cls.__dict__.items():
            if isinstance(value, Field):
                fields[name] = value
                if value.is_primarykey:
                    primarykey = value
            elif name == 'table_name':
                table_name = value
            elif name == 'table_prefix':
                table_prefix = value

        if table_name is None:
            table_name = cls.__default_table_name()

        if table_prefix:
            table_name = table_prefix + table_name

        if primarykey is None:
            fields['id'] = primarykey = PrimaryKey()

        cls.primarykey = primarykey
        cls.table_name = table_name
        cls.fields = fields

        for name, field in cls.fields.items():
            field.describe(name, cls)

        cls.runtime = Runtime(cls)

    def __default_table_name(cls):
        # default: 'User' => 'user', 'CuteCat' => 'cute_cat'
        def e(x, y):
            s = '_' if y.isupper() else ''
            return s.join((x, y))
        return reduce(e, list(cls.__name__)).lower()


class Model(MetaModel('NewBase', (object, ), {})):  # py3 compat

    single = True

    def __init__(self, *lst, **dct):
        self.data = {}

        for expr in lst:
            field, value = expr.left, expr.right
            self.data[field.name] = value

        self.data.update(dct)
        self._cache = self.data.copy()
        self.set_in_db(True)

    def set_in_db(self, boolean):
        self._in_db = boolean

    def __kwargs(func):
        @classmethod
        def _func(cls, *lst, **dct):
            lst = list(lst)
            if dct:
                lst.extend([cls.fields[k] == v for k, v in dct.items()])
            return func(cls, *lst)
        return _func

    @__kwargs
    def insert(cls, *lst, **dct):
        cls.runtime.set_values(lst)
        return InsertQuery(cls.runtime, cls)

    @__kwargs
    def update(cls, *lst, **dct):
        cls.runtime.set_set(lst)
        return UpdateQuery(cls.runtime, cls)

    @classmethod
    def select(cls, *lst):
        if not lst:
            lst = cls.fields.values()
        cls.runtime.set_select(lst)
        return SelectQuery(cls.runtime)

    @classmethod
    def delete(cls):
        return DeleteQuery(cls.runtime)
