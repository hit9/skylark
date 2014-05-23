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

    A micro python orm for mysql and sqlite.

    :author: Chao Wang (Hit9).
    :license: BSD.
"""


__version__ = '0.9.0'


__all__ = (
    '__version__',
    'SkylarkException',
    'UnSupportedDBAPI',
    'PrimaryKeyValueNotFound',
    'SQLSyntaxError',
    'ForeignKeyNotFound',
    'Database', 'database',
    'sql', 'SQL',
    'Field',
    'PrimaryKey',
    'ForeignKey',
    'compiler',
    'fn',
    'distinct', 'Distinct'
    'Model',
    'MultiModels', 'Models',
    'JoinModel'
)


import sys


if sys.hexversion < 0x03000000:
    PY_VERSION = 2
else:
    PY_VERSION = 3

if PY_VERSION == 3:
    from functools import reduce


# common operators (~100)
OP_OP = 0  # custom op
OP_LT = 1
OP_LE = 2
OP_GT = 3
OP_GE = 4
OP_EQ = 5
OP_NE = 6
OP_ADD = 7
OP_SUB = 8
OP_MUL = 9
OP_DIV = 10
OP_MOD = 11
OP_AND = 12
OP_OR = 13
OP_RADD = 27
OP_RSUB = 28
OP_RMUL = 29
OP_RDIV = 30
OP_RMOD = 31
OP_RAND = 32
OP_ROR = 33
OP_LIKE = 99

# special operators (100+)
OP_BETWEEN = 101
OP_IN = 102
OP_NOT_IN = 103

# runtimes
RT_ST = 1
RT_VL = 2
RT_SL = 3
RT_WH = 4
RT_GP = 5
RT_HV = 6
RT_OD = 7
RT_LM = 8
RT_JN = 9
RT_TG = 10
RT_FM = 11


# query types
QUERY_INSERT = 1
QUERY_UPDATE = 2
QUERY_SELECT = 3
QUERY_DELETE = 4


class SkylarkException(Exception):
    pass


class UnSupportedDBAPI(SkylarkException):
    pass


class PrimaryKeyValueNotFound(SkylarkException):
    pass


class SQLSyntaxError(SkylarkException):
    pass


class ForeignKeyNotFound(SkylarkException):
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


DBAPI_MAPPINGS = {
    'MySQLdb': MySQLdbAPI,
    'pymysql': PyMySQLAPI,
    'sqlite3': Sqlite3API,
}


DBAPI_LOAD_ORDER = ('MySQLdb', 'pymysql', 'sqlite3')


class DatabaseType(object):

    def __init__(self):
        self.dbapi = None
        self.conn = None
        self.configs = {}
        self.autocommit = None

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
        self.autocommit = configs.pop('autocommit', True)
        self.configs.update(configs)

        # close active connection on configs change
        if self.dbapi.conn_is_open(self.conn):
            self.dbapi.close_conn(self.conn)

    def connect(self):
        self.conn = self.dbapi.connect(self.configs)
        self.dbapi.set_autocommit(self.conn, self.autocommit)
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
        self.dbapi.execute_cursor(cursor, args)
        return cursor

    def execute_sql(self, sql):  # execute a sql object
        return self.execute(sql.literal, sql.params)

    def change(self, db):
        return self.dbapi.select_db(db, self.conn, self.configs)

    def set_autocommit(self, boolean):
        self.autocommit = boolean
        if self.dbapi.conn_is_open(self.conn):
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


class Leaf(object):

    def _e(op_type, invert=False):
        def e(self, right):
            if invert:
                return Expr(right, self, op_type)
            return Expr(self, right, op_type)
        return e

    __lt__ = _e(OP_LT)
    __le__ = _e(OP_LE)
    __gt__ = _e(OP_GT)
    __ge__ = _e(OP_GE)
    __eq__ = _e(OP_EQ)
    __ne__ = _e(OP_NE)

    __add__ = _e(OP_ADD)
    __sub__ = _e(OP_SUB)
    __mul__ = _e(OP_MUL)
    __div__ = _e(OP_DIV)
    __truediv__ = _e(OP_DIV)
    __mod__ = _e(OP_MOD)
    __and__ = _e(OP_AND)
    __or__ = _e(OP_OR)

    __radd__ = _e(OP_ADD, invert=True)
    __rsub__ = _e(OP_SUB, invert=True)
    __rmul__ = _e(OP_MUL, invert=True)
    __rdiv__ = _e(OP_DIV, invert=True)
    __rtruediv__ = _e(OP_DIV, invert=True)
    __rmod__ = _e(OP_MOD, invert=True)
    __rand__ = _e(OP_AND, invert=True)
    __ror__ = _e(OP_OR, invert=True)

    def like(self, pattern):
        return Expr(self, pattern, OP_LIKE)

    def between(self, left, right):
        return Expr(self, (left, right), OP_BETWEEN)

    def _in(self, *vals):
        return Expr(self, vals, OP_IN)

    def not_in(self, *vals):
        return Expr(self, vals, OP_NOT_IN)

    def op(self, op_str):
        def func(other):
            return Expr(self, other, OP_OP, op_str=op_str)
        return func


class SQL(Leaf):

    def __init__(self, literal, *params):
        self.literal = literal
        self.params = params

    def __repr__(self):
        return '<sql %r %r>' % (self.literal, self.params)

    @classmethod
    def format(cls, spec, *args):
        literal = spec % tuple(arg.literal for arg in args)
        params = sum([arg.params for arg in args], tuple())
        return cls(literal, *params)

    @classmethod
    def join(cls, sptr, seq):
        # seq maybe a generator, so cast it static to iter twice
        seq = tuple(seq)
        literal = sptr.join(sql.literal for sql in seq)
        params = sum([sql.params for sql in seq], tuple())
        return cls(literal, *params)

    def normalize(self):
        # let sql literal behave normal
        self.literal = ' '.join(self.literal.split())  # remove spaces
        # remove unnecessary parentheses
        size = len(self.literal)
        count = 0
        pairs = []

        for p in range(size):
            if self.literal[p] != '(':
                continue
            for q in range(p, size):
                if self.literal[q] == '(':
                    count += 1
                if self.literal[q] == ')':
                    count -= 1
                if count == 0:
                    break
            if count != 0:
                raise SQLSyntaxError  # unbalanced '()'
            pairs.append((p, q))

        blacklist = []

        for p, q in pairs:
            if (p + 1, q - 1) in pairs:
                blacklist.append(p)
                blacklist.append(q)

        self.literal = ''.join(v for k, v in enumerate(self.literal)
                               if k not in blacklist)


sql = SQL


class Expr(Leaf):

    def __init__(self, left, right, op_type, op_str=None):
        self.left = left
        self.right = right
        self.op_type = op_type
        self.op_str = op_str


class Alias(object):

    def __init__(self, name, inst):
        self.name = name
        self.inst = inst


class FieldDescriptor(object):

    def __init__(self, field):
        self.field = field

    def __get__(self, inst, type=None):
        if inst:
            return inst.data[self.field.name]
        return self.field

    def __set__(self, inst, val):
        inst.data[self.field.name] = val


class Field(Leaf):

    def __init__(self, is_primarykey=False, is_foreignkey=False):
        self.is_primarykey = is_primarykey
        self.is_foreignkey = is_foreignkey

    def describe(self, name, model):
        self.name = name
        self.model = model
        self.fullname = '%s.%s' % (model.table_name, name)
        setattr(model, name, FieldDescriptor(self))

    def alias(self, name):
        return Alias(name, self)


class PrimaryKey(Field):

    def __init__(self):
        super(PrimaryKey, self).__init__(is_primarykey=True)


class ForeignKey(Field):

    def __init__(self, reference):
        super(ForeignKey, self).__init__(is_foreignkey=True)
        self.reference = reference


class Function(Leaf):

    def __init__(self, name, *args):
        self.name = name
        self.args = args

    def alias(self, name):
        return Alias(name, self)


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

    def __init__(self, type, runtime):
        self.type = type
        self.sql = compiler.compile(self.type, runtime)
        runtime.reset_data()


class InsertQuery(Query):

    def __init__(self, runtime):
        super(InsertQuery, self).__init__(QUERY_INSERT, runtime)

    def execute(self):
        cursor = database.execute_sql(self.sql)
        last_insert_id = cursor.lastrowid
        rows_affected = cursor.rowcount
        cursor.close()
        if rows_affected:
            return last_insert_id


class UpdateQuery(Query):

    def __init__(self, runtime):
        super(UpdateQuery, self).__init__(QUERY_UPDATE, runtime)

    def execute(self):
        cursor = database.execute_sql(self.sql)
        rows_affected = cursor.rowcount
        cursor.close()
        return rows_affected


class SelectQuery(Query):

    def __init__(self, runtime):
        self.model = runtime.model
        self.nodes = runtime.data[RT_SL]
        super(SelectQuery, self).__init__(QUERY_SELECT, runtime)

    def execute(self):
        cursor = database.execute_sql(self.sql)
        result = SelectResult(tuple(cursor.fetchall()), self.model, self.nodes)
        cursor.close()
        return result

    def __iter__(self):
        result = self.execute()
        return iter(result.all())


class DeleteQuery(Query):

    def __init__(self, runtime):
        super(DeleteQuery, self).__init__(QUERY_DELETE, runtime)

    def execute(self):
        cursor = database.execute_sql(self.sql)
        rows_affected = cursor.rowcount
        cursor.close()
        return rows_affected


class SelectResult(object):

    def __init__(self, rows, model, nodes, rowcount=-1):
        self.rows = rows
        self.model = model
        # for sqlite3, DBAPI2 said rowcount on select will always be -1
        self.count = rowcount if rowcount >= 0 else len(rows)
        self._rows = (row for row in self.rows)

        # distinct should be the first select node if it exists
        if nodes and isinstance(nodes[0], Distinct):
            nodes = list(nodes[0].args) + nodes[1:]
        self.nodes = nodes

    def inst(self, model, row):
        inst = model()
        inst.set_in_db(True)

        for idx, node in enumerate(self.nodes):
            if isinstance(node, Field) and node.model is model:
                inst.data[node.name] = row[idx]
            if isinstance(node, Alias) and isinstance(node.inst, Field) \
                    and node.inst.model is model:
                setattr(inst, node.name, row[idx])
        return inst

    def __one(self, row):
        if self.model.single:
            return self.inst(self.model, row)
        return tuple(map(lambda m: self.inst(m, row), self.model.models))

    def one(self):
        try:
            row = next(self._rows)  # py2.6+/3.0+
        except StopIteration:
            return None
        return self.__one(row)

    def all(self):
        return tuple(map(self.__one, self.rows))

    def tuples(self):
        return self.rows


class Compiler(object):

    mappings = {
        OP_LT: '<',
        OP_LE: '<=',
        OP_GT: '>',
        OP_GE: '>=',
        OP_EQ: '=',
        OP_NE: '<>',
        OP_ADD: '+',
        OP_SUB: '-',
        OP_MUL: '*',
        OP_DIV: '/',
        OP_MOD: '%%',  # escape '%'
        OP_AND: 'and',
        OP_OR: 'or',
        OP_LIKE: 'like',
        OP_BETWEEN: 'between',
        OP_IN: 'in',
        OP_NOT_IN: 'not in',
    }

    def sql2sql(sql):
        return sql

    def query2sql(query):
        return sql.format('(%s)', query.sql)

    def alias2sql(alias):
        spec = '%%s as %s' % alias.name
        return sql.format(spec, compiler.sql(alias.inst))

    def field2sql(field):
        return sql(field.fullname)

    def function2sql(function):
        spec = '%s(%%s)' % function.name
        args = sql.join(', ', map(compiler.sql, function.args))
        return sql.format(spec, args)

    def distinct2sql(distinct):
        args = sql.join(', ', map(compiler.sql, distinct.args))
        return sql.format('distinct(%s)', args)

    def expr2sql(expr):
        if expr.op_str is None:
            op_str = compiler.mappings[expr.op_type]
        else:
            op_str = expr.op_str

        left = compiler.sql(expr.left)

        if expr.op_type < 100:  # common ops
            right = compiler.sql(expr.right)
        elif expr.op_type is OP_BETWEEN:
            right = sql.join(' and ', map(compiler.sql, expr.right))
        elif expr.op_type in (OP_IN, OP_NOT_IN):
            vals = sql.join(', ', map(compiler.sql, expr.right))
            right = sql.format('(%s)', vals)

        spec = '%%s %s %%s' % op_str

        if expr.op_type in (OP_AND, OP_OR):
            spec = '(%s)' % spec

        return sql.format(spec, left, right)

    conversions = {
        SQL: sql2sql,
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

    def jn2sql(lst):
        prefix, main, join, expr = lst

        prefix = '' if prefix is None else '%s ' % prefix

        if expr is None:
            foreignkey = _detect_bridge(main, join)
            expr = foreignkey == foreignkey.reference

        spec = '%sjoin %s on %%s' % (prefix, join.table_name)
        return sql.format(spec, compiler.sql(expr))

    def od2sql(lst):
        node, desc = lst
        spec = 'order by %%s%s' % (' desc' if desc else '')
        return sql.format(spec, compiler.sql(node))

    def gp2sql(lst):
        spec = 'group by %s'
        arg = sql.join(', ', map(compiler.sql, lst))
        return sql.format(spec, arg)

    def hv2sql(lst):
        spec = 'having %s'
        arg = sql.join(' and ', map(compiler.sql, lst))
        return sql.format(spec, arg)

    def wh2sql(lst):
        spec = 'where %s'
        arg = sql.join(' and ', map(compiler.sql, lst))
        return sql.format(spec, arg)

    def sl2sql(lst):
        return sql.join(', ', map(compiler.sql, lst))

    def lm2sql(lst):
        offset, rows = lst
        literal = 'limit %s%s' % (
            '%s, ' % offset if offset is not None else '', rows)
        return sql(literal)

    def st2sql(lst):
        pairs = [
            sql.format('%s=%%s' % expr.left.name, compiler.sql(expr.right))
            for expr in lst]
        return sql.join(', ', pairs)

    def vl2sql(lst):
        keys = ', '.join([expr.left.name for expr in lst])
        vals = map(compiler.sql, [expr.right for expr in lst])
        spec = '(%s) values (%%s)' % keys
        arg = sql.join(', ', vals)
        return sql.format(spec, arg)

    def tg2sql(lst):
        args = map(sql, [m.table_name for m in lst])
        return sql.join(', ', args)

    def fm2sql(lst):
        args = map(sql, [m.table_name for m in lst])
        return sql.join(', ', args)

    rt_conversions = {
        RT_OD: od2sql,
        RT_GP: gp2sql,
        RT_HV: hv2sql,
        RT_WH: wh2sql,
        RT_SL: sl2sql,
        RT_LM: lm2sql,
        RT_ST: st2sql,
        RT_VL: vl2sql,
        RT_JN: jn2sql,
        RT_TG: tg2sql,
        RT_FM: fm2sql,
    }

    patterns = {
        QUERY_INSERT: ('insert into %s %s', (RT_TG, RT_VL)),
        QUERY_UPDATE: ('update %s set %s %s', (RT_TG, RT_ST, RT_WH)),
        QUERY_SELECT: ('select %s from %s %s %s %s %s %s %s', (
            RT_SL, RT_FM, RT_JN, RT_WH, RT_GP, RT_HV, RT_OD, RT_LM)),
        QUERY_DELETE: ('delete %s from %s %s', (RT_TG, RT_FM, RT_WH))
    }

    def compile(self, type, runtime):
        pattern = self.patterns[type]

        spec, rts = pattern

        args = []

        for tp in rts:
            data = runtime.data[tp]
            if data:
                args.append(self.rt_conversions[tp](data))
            else:
                args.append(sql(''))

        sq = sql.format(spec, *args)
        sq.normalize()
        return sq


compiler = Compiler()


class Runtime(object):

    RUNTIMES = (
        RT_ST,  # update set
        RT_VL,  # insert values
        RT_SL,  # select fields
        RT_WH,  # where
        RT_GP,  # group by
        RT_HV,  # having
        RT_OD,  # order by
        RT_LM,  # limit
        RT_JN,  # join (inner, left, inner)
        RT_TG,  # target table
        RT_FM,  # from table
    )

    def __init__(self, model):
        self.model = model
        self.reset_data()

    def reset_data(self):
        self.data = dict((k, []) for k in self.RUNTIMES)

    def _e(tp):
        def e(self, lst):
            self.data[tp] = list(lst)
        return e

    set_st = _e(RT_ST)

    set_vl = _e(RT_VL)

    set_sl = _e(RT_SL)

    set_wh = _e(RT_WH)

    set_gp = _e(RT_GP)

    set_hv = _e(RT_HV)

    set_od = _e(RT_OD)

    set_lm = _e(RT_LM)

    set_jn = _e(RT_JN)

    set_tg = _e(RT_TG)

    set_fm = _e(RT_FM)


class MetaModel(type):

    def __init__(cls, name, bases, attrs):
        # table_name is not inheritable
        table_name = cls.__dict__.get(
            'table_name', cls.__default_table_name())
        # table_prefix is inheritable
        table_prefix = getattr(cls, 'table_prefix', None)
        if table_prefix:
            table_name = table_prefix + table_name
        cls.table_name = table_name
        cls.table_prefix = table_prefix

        primarykey = None
        fields = {}
        for key, val in cls.__dict__.items():
            if isinstance(val, Field):
                fields[key] = val
                if val.is_primarykey:
                    primarykey = val
        if primarykey is None:
            fields['id'] = primarykey = PrimaryKey()
        for name, field in fields.items():
            field.describe(name, cls)

        cls.fields = fields
        cls.primarykey = primarykey
        cls.runtime = Runtime(cls)

    def __default_table_name(cls):
        def _e(x, y):
            s = '_' if y.isupper() else ''
            return s.join((x, y))
        return reduce(_e, list(cls.__name__)).lower()

    def __contains__(cls, inst):
        if isinstance(inst, cls):
            if inst._in_db:
                return True
            query = cls.where(**inst.data).select(fn.count(cls.primarykey))
            result = query.execute()
            if result.tuples()[0][0] > 0:
                return True
        return False

    def __and__(cls, other):
        return JoinModel(cls, other)


class Model(MetaModel('NewBase', (object, ), {})):  # py3 compat

    single = True

    def __init__(self, *lst, **dct):
        self.data = {}

        for expr in lst:
            field, val = expr.left, expr.right
            self.data[field.name] = val

        self.data.update(dct)
        self._cache = self.data.copy()
        self.set_in_db(False)

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
        cls.runtime.set_vl(lst)
        cls.runtime.set_tg([cls])
        return InsertQuery(cls.runtime)

    @__kwargs
    def update(cls, *lst, **dct):
        cls.runtime.set_st(lst)
        cls.runtime.set_tg([cls])
        return UpdateQuery(cls.runtime)

    @classmethod
    def select(cls, *lst):
        if not lst:
            lst = cls.fields.values()
        cls.runtime.set_sl(lst)
        cls.runtime.set_fm([cls])
        return SelectQuery(cls.runtime)

    @classmethod
    def delete(cls):
        cls.runtime.set_fm([cls])
        return DeleteQuery(cls.runtime)

    @classmethod
    def create(cls, *lst, **dct):
        query = cls.insert(*lst, **dct)
        id = query.execute()

        if id is not None:
            dct[cls.primarykey.name] = id
            inst = cls(*lst, **dct)
            inst.set_in_db(True)
            return inst
        return None

    @__kwargs
    def where(cls, *lst, **dct):
        cls.runtime.set_wh(lst)
        return cls

    @classmethod
    def at(cls, id):
        return cls.where(cls.primarykey == id)

    @classmethod
    def orderby(cls, field, desc=False):
        cls.runtime.set_od((field, desc))
        return cls

    @classmethod
    def groupby(cls, *lst):
        cls.runtime.set_gp(lst)
        return cls

    @classmethod
    def having(cls, *lst):
        cls.runtime.set_hv(lst)
        return cls

    @classmethod
    def limit(cls, rows, offset=None):
        cls.runtime.set_lm((offset, rows))
        return cls

    @classmethod
    def join(cls, model, on=None, prefix=None):
        cls.runtime.set_jn((prefix, cls, model, on))
        return cls

    @classmethod
    def left_join(cls, model, on=None):
        return cls.join(model, on=on, prefix='left')

    @classmethod
    def right_join(cls, model, on=None):
        return cls.join(model, on=on, prefix='right')

    @classmethod
    def full_join(cls, model, on=None):
        return cls.join(model, on=on, prefix='full')

    @classmethod
    def findone(cls, *lst, **dct):
        query = cls.where(*lst, **dct).select()
        result = query.execute()
        return result.one()

    @classmethod
    def findall(cls, *lst, **dct):
        query = cls.where(*lst, **dct).select()
        result = query.execute()
        return result.all()

    @classmethod
    def getone(cls):
        return cls.select().execute().one()

    @classmethod
    def getall(cls):
        return cls.select().execute().all()

    @property
    def _id(self):
        return self.data.get(type(self).primarykey.name, None)

    def save(self):
        model = type(self)

        if not self._in_db:  # insert
            id = model.insert(**self.data).execute()

            if id is not None:
                self.data[model.primarykey.name] = id
                self.set_in_db(True)
                self._cache = self.data.copy()  # sync cache on saving
            return id
        else:  # update
            dct = dict(set(self.data.items()) - set(self._cache.items()))

            if self._id is None:
                raise PrimaryKeyValueNotFound

            if dct:
                query = model.at(self._id).update(**dct)
                rows_affected = query.execute()
            else:
                rows_affected = 0
            self._cache = self.data.copy()
            return rows_affected

    def destroy(self):
        if self._in_db:
            if self._id is None:
                raise PrimaryKeyValueNotFound
            result = type(self).at(self._id).delete().execute()
            if result:
                self.set_in_db(False)
            return result
        return None

    def aggregator(name):
        @classmethod
        def _func(cls, arg=None):
            if arg is None:
                arg = cls.primarykey
            function = Function(name, arg)
            query = cls.select(function)
            result = query.execute()
            return result.tuples()[0][0]
        return _func

    count = aggregator('count')

    sum = aggregator('sum')

    max = aggregator('max')

    min = aggregator('min')

    avg = aggregator('avg')


class MultiModels(object):

    single = False

    def __init__(self, *models):
        self.models = models
        self.runtime = Runtime(self)

    def select(self, *lst):
        if not lst:
            lst = sum([list(m.fields.values()) for m in self.models], [])
        self.runtime.set_sl(lst)
        self.runtime.set_fm(self.models)
        return SelectQuery(self.runtime)

    def delete(self, *targets):  # default target: all (mysql only)
        if not targets:
            targets = self.models
        self.runtime.set_fm(self.models)
        self.runtime.set_tg(targets)
        return DeleteQuery(self.runtime)

    def update(self, *lst):
        self.runtime.set_fm(self.models)
        self.runtime.set_set(lst, {})
        return UpdateQuery(self.runtime)

    def where(self, *lst):
        self.runtime.set_wh(lst)
        return self

    def orderby(self, field, desc=False):
        self.runtime.set_od((field, desc))
        return self

    def groupby(self, *lst):
        self.runtime.set_gp(lst)
        return self

    def having(self, *lst):
        self.runtime.set_hv(lst)
        return self

    def limit(self, rows, offset=None):
        self.runtime.set_lm((offset, rows))
        return self

    def findone(self, *lst):
        query = self.where(*lst).select()
        result = query.execute()
        return result.one()

    def findall(self, *lst):
        query = self.where(*lst).select()
        result = query.execute()
        return result.all()

    def getone(self):
        return self.select().execute().one()

    def getall(self):
        return self.select().execute().all()


Models = MultiModels


class JoinModel(MultiModels):

    def __init__(self, main, join):
        super(JoinModel, self).__init__(main, join)
        self.bridge = _detect_bridge(main, join)

    def build_bridge(func):
        def _func(self, *args, **kwargs):
            self.runtime.data[RT_WH].append(
                self.bridge == self.bridge.reference)
            return func(self, *args, **kwargs)
        return _func

    @build_bridge
    def select(self, *lst):
        return super(JoinModel, self).select(*lst)

    @build_bridge
    def update(self, *lst):
        return super(JoinModel, self).update(*lst)

    @build_bridge
    def delete(self, *targets):
        return super(JoinModel, self).delete(*targets)


def _detect_bridge(m, n):
    # detect foreignkey point between m and n
    models = (m, n)

    for i, k in enumerate(models):
        for field in k.fields.values():
            j = models[1 ^ i]
            if field.is_foreignkey and field.reference is j.primarykey:
                return field
    raise ForeignKeyNotFound
