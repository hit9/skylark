# -*- coding: utf-8 -*-
#   ____ _   _ ____  ____
#  / ___| | | |  _ \|  _ \  _ __  _   _
# | |   | | | | |_) | | | || '_ \| | | |
# | |___| |_| |  _ <| |_| || |_) | |_| |
#  \____|\___/|_| \_\____(_) .__/ \__, |
#                         |_|    |___/
#
# Permission to use, copy, modify,
# and distribute this software for any purpose with
# or without fee is hereby granted,
# provided that the above copyright notice
# and this permission notice appear in all copies.
#

"""
    CURD.py
    ~~~~~~~

    Tiny Python ORM for MySQL.

    :copyright: (c) 2014 by Chao Wang (Hit9).
    :license: BSD.
"""


__version__ = '0.4.1'


import types
import MySQLdb
from datetime import datetime, time, date, timedelta
from _mysql import string_literal, NULL, escape_sequence, escape_dict

# operators
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

# query types
QUERY_INSERT = 20
QUERY_UPDATE = 21
QUERY_SELECT = 22
QUERY_DELETE = 23

# supported sql functions
# {{{ -------- aggregate functions
FUNC_COUNT = 31
FUNC_SUM = 32
FUNC_MAX = 33
FUNC_MIN = 34
FUNC_AVG = 35
# ---------- }}}
# {{{ ------- scalar functions
FUNC_UCASE = 41
FUNC_LCASE = 42
# ---------- }}}

DATA_ENCODING = 'utf8'  # user python code encoding


class CURDException(Exception):
    """There was an ambiguous exception occurred"""
    pass


class UnSupportedType(CURDException):
    """This value's type is unsupported now"""
    pass


class ForeignKeyNotFound(CURDException):
    """Foreign key was not found in main model"""
    pass


class PrimaryKeyValueNotFound(CURDException):
    """Primarykey value was not found in this instance"""
    pass


class Database(object):
    """Database connection manager.

    attributes:

      configs
        dict object, current configuration for connection with default
        values

      autocommit
        boolean,  disables or enables the default autocommit mode for the
        current session, default: True

      conn
        mysql connection object, the `<_mysql.connection object>`.
    """

    # configuration for connection with default values
    configs = {
        'host': 'localhost',
        'port': 3306,
        'db': '',
        'user': '',
        'passwd': '',
        'charset': 'utf8'
    }

    # It is strongly recommended that you set this `True`
    autocommit = True

    # mysql connection object
    conn = None

    @classmethod
    def config(cls, autocommit=True, **configs):
        """
        Configure the database connection.

        The connection will be auto established with these configs.

        Keyword parameters for this method:

          host
            string, host to connect

          user
            string, user to connect as

          passwd
            string, password for this user

          db
            string, database to use

          port
            integer, TCP/IP port to connect

          charset
            string, charset of connection

        See the MySQLdb documentation for more information,
        the parameters of `MySQLdb.connect` are all supported.
        """
        cls.configs.update(configs)
        cls.autocommit = autocommit

        if cls.conn and cls.conn.open:  # close active connection
            cls.conn.close()

    @classmethod
    def connect(cls):
        """Connect to database with current `Database.configs`, always creates
        a new connection to mysql.

        CURD.py will auto establish a singleton connection once running a query
        , you don't have to call this method to connect to database manually.
        """
        cls.conn = MySQLdb.connect(**cls.configs)
        cls.conn.autocommit(cls.autocommit)

    @classmethod
    def get_conn(cls):
        """Get current MySQL connection object.

        If current connection is open and working normally, return this
        connection object; else, creates a new connection and return it.
        """

        if not cls.conn or not cls.conn.open:
            cls.connect()

        try:
            cls.conn.ping()  # ping to test if the current conn is working
        except MySQLdb.OperationalError:
            cls.connect()

        return cls.conn

    @classmethod
    def execute(cls, sql):
        """Execute a single raw query.

        parameters:
          sql
            string, sql command to be executed

        return:
          `MySQLdb.cursors object`

        sample::

            >>> Database.execute('select * from user')
            <MySQLdb.cursors.Cursor object at 0xb710aaec>
        """
        cursor = cls.get_conn().cursor()
        cursor.execute(sql)
        return cursor

    @classmethod
    def change(cls, db):
        """Switch database to `db`.

        parameters:
          db
            string, database to use

        sample::

            >>> Database.change('mydb')
            >>> Database.select_db('mydb')  # alias
        """
        cls.configs['db'] = db

        if cls.conn and cls.conn.open:
            cls.conn.select_db(db)

    select_db = change  # alias of `Database.change`


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
        return self.__attrs() == self.__attrs()

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
    """Field object, mapping to field in mysql table, i.e. `User.name`.

    attributes:

      is_primarykey
        boolean, if this field a primarykey

      is_foreignkey
        boolean, if this field a foreignkey

      name
        string, field's shortname, i.e `User.name`'s name is `name`

      fullname
        string, field's fullname, i.e `User.name`'s fullname is `user.name`

      model
        Model object, the model this field was bound.

    """

    def __init__(self, is_primarykey=False, is_foreignkey=False):
        self.is_primarykey = is_primarykey
        self.is_foreignkey = is_foreignkey

    def describe(self, name, model):
        self.name = name
        self.model = model
        self.fullname = '{table}.{field}'.format(table=self.model.table_name,
                                                 field=self.name)
        setattr(model, name, FieldDescriptor(self))  # describe this attribute

    def __repr__(self):
        return '<%s %r>' % (type(self).__name__, self.fullname)

    def like(self, pattern):
        """
        parameters

          pattern
            string, pattern to like

        sample::
            >>> User.name.like('%Amy%')
        """
        return Expr(self, pattern, OP_LIKE)

    def between(self, left, right):
        """
        parameters

          left, right
            string/integer/..

        sample::
            >>> User.age.between(13, 17)
        """
        return Expr(self, (left, right), OP_BETWEEN)

    def _in(self, *values):
        """
        parameters

          *values
            string/integer/sub_query/..

        sample::
            >>> User.age._in(1, 3, 5, 7)
            >>> User.id._in(Post.select(Post.user_id))
        """
        return Expr(self, values, OP_IN)

    def not_in(self, *values):
        """
        parameters

          *values:
            string/integer/sub_query/..

        sample::
            >>> User.age._in(1, 3, 5, 7)
            >>> User.id._in(Post.select(Post.user_id))
        """
        return Expr(self, values, OP_NOT_IN)


class PrimaryKey(Field):
    """PrimaryKey object, fields which `is_primarykey` set `True`."""

    def __init__(self):
        super(PrimaryKey, self).__init__(is_primarykey=True)


class ForeignKey(Field):
    """ForeignKey object, fields which `is_foreignkey` set `True`

    parameters

      point_to
        PrimaryKey object, the primary key this foreignkey referenced to.
    """

    def __init__(self, point_to):
        super(ForeignKey, self).__init__(is_foreignkey=True)
        self.point_to = point_to


class Function(Leaf):
    """Function object, i.e. `count(User.id)`, `max(User.age)`.

    CURD.py only supports scalar functions (`lcase`, `ucase`..)
    and aggregate functions(`count`, `max`..).

    attributes

      field
        Field object, field object this function functions

      func_type
        integer, this function's type

      name
        string, this function's shortname, i.e. `count(user.name)`

      fullname
        string, this function's fullname, i.e. `count_of_name`

      model
        Model object, model its field was bound
    """

    FUNC_MAPPINGS = {
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
        # the name appeared in SQL string
        self.fullname = '%s(%s)' % (Function.FUNC_MAPPINGS[self.func_type],
                                    field.fullname)
        # the name in the python codes
        self.name = '%s_of_%s' % (Function.FUNC_MAPPINGS[self.func_type],
                                  field.name)
        self.model = self.field.model

    def __repr__(self):
        return 'Function %r' % self.fullname


class Fn(object):
    """API class with supported functions.

    sample::

        >>> Fn.count(User.id)
        <Function 'count(user.id)'>

    """

    def fn(func_type):
        @classmethod
        def _fn(cls, field):
            return Function(field, func_type)
        return _fn

    count = fn(FUNC_COUNT)

    sum = fn(FUNC_SUM)

    max = fn(FUNC_MAX)

    min = fn(FUNC_MIN)

    avg = fn(FUNC_AVG)

    ucase = fn(FUNC_UCASE)

    lcase = fn(FUNC_LCASE)


class Compiler(object):
    """Compile expressions and sequence of methods to SQL strings"""

    # operator mapping
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

    # sql patterns
    SQL_PATTERNS = {
        QUERY_INSERT: 'insert into {target}{set}',
        QUERY_UPDATE: 'update {target}{set}{where}',
        QUERY_SELECT: 'select{distinct} {select} from {from}{where}{groupby}{having}{orderby}{limit}',
        QUERY_DELETE: 'delete {target} from {from}{where}'
    }

    expr_cache = {}  # dict to cache parsed expr

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
        return string_literal('%d %d:%d:%d' % (data.days, hours, minutes, seconds))

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

        if isinstance(side, (Field, Function)):  # field
            return side.fullname
        elif isinstance(side, Expr):  # expression
            return Compiler.parse_expr(side)
        elif isinstance(side, Query):  # sub query
            return '(%s)' % side.sql
        elif type(side) in Compiler.conversions:  # common value
            return Compiler.conversions[type(side)](side)
        else:  # unsupported
            raise UnSupportedType("Unsupported type '%s' in one side of some"
                                  " expression" % str(type(side)))

    @staticmethod
    def parse_expr(expr):

        cache = Compiler.expr_cache

        # check cache at first
        if expr in cache:  # `in` statement uses `__hash__` and then `__eq__`
            return cache[expr]

        # make alias
        l, op, r = expr.left, expr.op, expr.right
        OP_MAPPING = Compiler.OP_MAPPING
        tostr = Compiler.__parse_expr_one_side

        string = None

        if op in OP_MAPPING:
            string = tostr(l) + OP_MAPPING[op] + tostr(r)
        elif op is OP_BETWEEN:
            string = '%s between %s and %s' % (tostr(l), tostr(r[0]), tostr(r[1]))
        elif op in (OP_IN, OP_NOT_IN):
            string = '%s%s in (%s)' % (
                tostr(l), ' not' if op is OP_NOT_IN else '', ', '.join(tostr(value) for value in r)
            )

        cache[expr] = string  # set cache

        return string

    @staticmethod
    def parse_orderby(lst):
        if not lst:
            return ''

        field, desc = lst

        if desc:
            return ' order by %s desc' % field.fullname
        else:
            return ' order by %s' % field.fullname

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
            Compiler.parse_expr(expr) for expr in lst
        ))

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

        if offset is None:
            return ' limit %s' % rows
        else:
            return ' limit %s, %s' % (offset, rows)

    @staticmethod
    def parse_set(lst):
        return ' set %s' % (', '.join(
            Compiler.parse_expr(expr) for expr in lst
        ))

    @staticmethod
    def parse_distinct(boolean):
        return ' distinct' if boolean else ''

    @staticmethod
    def gen_sql(runtime, query_type, target_model=None):
        """
        Generate SQL from runtime information.

        parameters:
          runtime
            Runtime object, runtime instance
          query_type
            macros, query type, the QUERY_**:
          target_model
            Model object, model to delete, update, select or insert
        """

        from_table = runtime.model.table_name

        # if target_model not given, use from_table instead
        if target_model is None:
            target_model = runtime.model

        target_table = target_model.table_name

        data = runtime.data  # alias

        # quick mark for parse time functions
        _where = Compiler.parse_where(data['where'])
        _set = Compiler.parse_set(data['set'])
        _orderby = Compiler.parse_orderby(data['orderby'])
        _select = Compiler.parse_select(data['select'])
        _limit = Compiler.parse_limit(data['limit'])
        _groupby = Compiler.parse_groupby(data['groupby'])
        _having = Compiler.parse_having(data['having'])
        _distinct = Compiler.parse_distinct(data['distinct'])

        pattern = Compiler.SQL_PATTERNS[query_type]

        SQL = pattern.format(**{
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

        return SQL


class Runtime(object):

    def __init__(self, model=None):
        self.model = model
        self.data = {}.fromkeys(
            ('where', 'set', 'orderby', 'select', 'limit', 'groupby', 'having', 'distinct'),
            None)
        self.reset_data()

    def reset_data(self):
        dct = dict((key, []) for key in self.data.keys())
        dct['distinct'] = False
        self.data.update(dct)

    def __repr__(self):
        return '<Runtime %r>' % self.data

    def set_orderby(self, field_desc):
        self.data['orderby'] = list(field_desc)

    def set_groupby(self, lst):
        self.data['groupby'] = list(lst)

    def set_having(self, lst):
        self.data['having'] = list(lst)

    def set_limit(self, offset_rows):
        self.data['limit'] = list(offset_rows)

    def set_select(self, fields):
        flst = list(fields)

        if not flst:
            flst = self.model.get_fields()  # select all
        self.data['select'] = list(set(flst))  # remove duplicates

    def set_where(self, lst, dct):
        lst = list(lst)

        if self.model.single:  # Models objects cannot use dct as arg
            fields = self.model.fields
            lst.extend(fields[k] == v for k, v in dct.iteritems())

        self.data['where'] = lst

    def set_set(self, lst, dct):
        lst = list(lst)

        if self.model.single:
            fields = self.model.fields
            primarykey = self.model.primarykey
            lst.extend(fields[k] == v for k, v in dct.iteritems())
        self.data['set'] = lst

    def set_distinct(self, boolean):
        self.data['distinct'] = boolean


class Query(object):

    def __init__(self, query_type, runtime, target_model=None):
        self.query_type = query_type
        self.sql = Compiler.gen_sql(runtime, self.query_type, target_model)
        runtime.reset_data()  # !important: clean runtime right on this query initialized

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
    """Select query result.

    methods:
      fetchone,  fetch a single row each time
      fetchall,  fetch all rows at a time

    attributes:
      count,  results rowcount from mysql
    """

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
        """Fetch a single row each time"""
        row = self.cursor.fetchone()

        if row is None:
            return None

        if self.model.single:
            return self.__instance_from_db(self.model, row)
        else:
            return tuple(self.__instance_from_db(m, row) for m in self.model.models)

    def fetchall(self):
        """Fetch all rows at a time"""
        rows = self.cursor.fetchall()

        if self.model.single:
            for row in rows:
                yield self.__instance_from_db(self.model, row)
        else:
            for row in rows:
                yield tuple(self.__instance_from_db(m, row) for m in self.model.models)

    @property
    def count(self):
        return self.cursor.rowcount


class MetaModel(type):

    def __init__(cls, name, bases, attrs):

        table_name = None
        primarykey = None
        fields = {}  # {field_name: field}


        # lookup table_name, fields, primarykey from `cls.__dict__`
        for name, value in cls.__dict__.iteritems():
            if isinstance(value, Field):
                fields[name] = value

                if value.is_primarykey:
                    primarykey = value

            elif name == 'table_name':
                table_name = value

        if table_name is None:
            # default table_name. User => 'user', 'CuteCat' => 'cute_cat'
            table_name = reduce(
                lambda x, y: ('_' if y.isupper() else '').join((x, y)),
                list(cls.__name__)).lower()

        if primarykey is None:
            primarykey = PrimaryKey()   # default: `id`
            fields['id'] = primarykey

        cls.primarykey = primarykey
        cls.table_name = table_name
        cls.fields = fields

        # describe this cls's fields
        for name, field in cls.fields.iteritems():
            field.describe(name, cls)

        cls.runtime = Runtime(cls)

    def __and__(self, join):
        return JoinModel(self, join)

    def __contains__(self, obj):
        """To test if some instance is in table.

        sample usage::

            >>> user = User(name='jack')
            >>> user in User
            True
        """
        if isinstance(obj, self):
            query = self.where(**obj.data).select()
            result = query.execute()
            if result.count:
                return True
        return False


class Model(object):
    """
    Model object, mysql tables are mapped to models, i.e. table 'user' => `User`

    Model(*expressions, **values)

    instantiation parameters:

      expressions
        Expr objects, e.g. User(User.name == "Join")

      values
        name to value mappings, e.g. User(name="Join")

    sample instantiation::

        >>> user = User(name='jack', age=13, email='jack@gmail.com')
        >>> user = User(User.name == 'jack', age=13)

    instance attributes:

      data
        dict, data in this instance

      _id
        string/integer/.., value of this instance's primarykey

    """

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
        """Get this model's fields list."""
        return cls.fields.values()

    @classmethod
    def insert(cls, *lst, **dct):
        """Create a `insert` query.

        parameters:
          lst
            list, Expr objects, i.e. `User.insert(User.name=='jack')`
          dct
            dict, data mappings, i.e. `User.insert(name='jack')`

        return:
          InsertQuery object.

        sample::

            >>> User.insert(name='jack')
            <InsertQuery "insert into user set user.name = 'jack'">
        """
        cls.runtime.set_set(lst, dct)
        return InsertQuery(cls.runtime)

    @classmethod
    def select(cls, *flst):
        """Create a `select` query.

        parameters:
          flst
            list, Field or Function objects.

        return:
          SelectQuery object.

        sample::

            >>> User.select(User.id)
            <SelectQuery 'select user.id from user'>
            >>> User.where(User.id > 3).select()
            <SelectQuery "select user.email, user.id, user.name from user where user.id > '3'">
        """
        cls.runtime.set_select(flst)
        return SelectQuery(cls.runtime)

    @classmethod
    def update(cls, *lst, **dct):
        """Create a `update` query.

        parameters:
          lst
            list, Expr objects.
          dct
            dict, data mappings.

        return:
          UpdateQuery object.

        sample::

            >>> User.at(3).update(name='amy')
            <UpdateQuery "update user set user.name = 'amy' where user.id = '3'">

        """
        cls.runtime.set_set(lst, dct)
        return UpdateQuery(cls.runtime)

    @classmethod
    def create(cls, *lst, **dct):
        """Insert one new record into database and return the instance.

        parameters:
          lst
            list, Expr objects
          dct
            dict, data mappings

        return value:
          - on success: model's instance
          - on failure: None

        sample::

            >>> User.create(name='jack')
            <models.User object at 0xb70e0d6c>
        """
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
        """Create a `delete` query.

        return:
          DeleteQuery object.

        sample::

            >>> User.at(1).delete()
            <DeleteQuery "delete user from user where user.id = '1'">
        """
        return DeleteQuery(cls.runtime)

    @classmethod
    def where(cls, *lst, **dct):
        """The `where claause` in sql.

        parameters:
          lst
            list, Expr objects
          dct
            dict, data mappings

        sample::

            >>> User.where(User.name.like('%a')).select(User.id)
            <SelectQuery "select user.id from user where user.name like '%a'">
            >>> User.where(User.id <= 15).select(User.id)
            <SelectQuery "select user.id from user where user.id <= '15'">
            >>> User.where(name='jack').select(User.id)
            <SelectQuery "select user.id from user where user.name = 'jack'">
        """
        cls.runtime.set_where(lst, dct)
        return cls

    @classmethod
    def at(cls, _id):
        """Equal to `where(model.primarykey == _id)`.

        sample::

            >>> User.at(5).select(User.id)
            <SelectQuery "select user.id from user where user.id = '5'">
        """
        return cls.where(cls.primarykey == _id)

    @classmethod
    def orderby(cls, field, desc=False):
        """The `order by field [desc]` in sql.

        parameters:
          field
            Field object, the field to order by
          desc
            boolean, if desc? default: False

        return:
          this model

        sample::

            >>> User.orderby(User.id, desc=True).select()
            <SelectQuery 'select user.email, user.id, user.name from user order by user.id desc '>
        """
        cls.runtime.set_orderby((field, desc))
        return cls

    @classmethod
    def groupby(cls, *lst):
        """The `group  by` in sql.

        parameters:
          lst
            list, fields to group by

        return:
          this model

        sample::

            >>> query = User.groupby(User.name).select(User.id, User.name)
            >>> query.sql
            'select user.name, user.id from user group by user.name'
        """
        cls.runtime.set_groupby(lst)
        return cls

    @classmethod
    def having(cls, *lst):
        """The `having` in sql.

        parameters:
          lst
            list, Expr objects

        return:
          this model

        sample::

            >>> query = User.groupby(User.name).having(Fn.count(User.id) > 3).select(User.id, User.name)
            >>> query.sql
            "select user.name, user.id from user group by user.name having count(user.id) > '3'"
        """
        cls.runtime.set_having(lst)
        return cls

    @classmethod
    def limit(cls, rows, offset=None):
        """The `limit` in sql.

        parameters:
          rows
            integer, rows count to select
          offset
            integer, offset rows count, default: None

        return:
          this model

        sample::

            >>> query = User.limit(2, offset=1).select()
            >>> query.sql
            'select user.id, user.name, user.email from user limit 1, 2 '
        """
        cls.runtime.set_limit((offset, rows))
        return cls

    @classmethod
    def distinct(cls):
        """Distinct select results.

        sample::

            >>> [user.name for user in User.distinct().select(User.name)]
            [u'jack', u'tom']
        """
        cls.runtime.set_distinct(True)
        return cls

    #  ------------------ {{{select shortcuts

    @classmethod
    def findone(cls, *lst, **dct):
        """Fetch one result from database, equal to
        `Model.where(*lst, **dct).select().execute().fetchone()`.
        Return a single instance of this model."""
        query = cls.where(*lst, **dct).select()
        result = query.execute()
        return result.fetchone()

    @classmethod
    def findall(cls, *lst, **dct):
        """Fetch all results from database, equal to
        `Model.where(*lst, **dct).select().execute().fetchall()`.
        Return a tuple of instances of this model."""
        query = cls.where(*lst, **dct).select()
        result = query.execute()
        return result.fetchall()

    @classmethod
    def getone(cls):
        """Equal to `Model.select().execute().fetchone()`"""
        return cls.select().execute().fetchone()

    @classmethod
    def getall(cls):
        """Equal to `Model.select().execute().fetchall()`"""
        return cls.select().execute().fetchall()

    # ------------ select shortcuts }}}

    @property
    def _id(self):
        return self.data.get(type(self).primarykey.name, None)

    def set_in_db(self, boolean):
        self._in_db = boolean

    def save(self):
        """Save this instance to database, if this instance is created/select
        from database, update it; else if this instance is new to database,
        insert it into table.

        sample::

            >>> user = User.getone()
            >>> user.name = 'NewName'
            >>> user.save()  # update
            1L

            >>> user = User(name='NewPerson')
            >>> user.save()  # insert
            1L
        """
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

            if self._id is None:
                raise PrimaryKeyValueNotFound  # need its primarykey value to track this instance

            if dct:
                query = model.at(self._id).update(**dct)
                rows_affected = query.execute()
            else:
                rows_affected = 0L
            self._cache = self.data.copy()  # sync cache after saving
            return rows_affected

    def destroy(self):
        """Delete this instance if it came from database.

        Equal to `Model.at(id).delete().execute()`

        return:
          - on success: rows count deleted
          - on failure: None

        exceptions:

          PrimaryKeyValueNotFound
            this method needs instance's primarykey to delete

        sample::

            >>> user = User.getone()
            >>> user.destroy()
            1L
        """
        if self._in_db:
            if self._id is None:
                raise PrimaryKeyValueNotFound  #! need primarykey to track this instance
            return type(self).at(self._id).delete().execute()
        return None

    def fn(func_type):
        """Non-API functions factory."""
        @classmethod
        def _fn(cls, field=None):
            if field is None:
                field = cls.primarykey
            func = Function(field, func_type)
            query = cls.select(func)
            result = query.execute()
            instance = result.fetchone()
            return getattr(instance, func.name)
        return _fn

    count = fn(FUNC_COUNT)

    sum = fn(FUNC_SUM)

    max = fn(FUNC_MAX)

    min = fn(FUNC_MIN)

    avg = fn(FUNC_AVG)


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
                "Foreign key references to "
                "'%s' not found in '%s'" % (join.__name__, main.__name__)
            )

    def brigde_wrapper(func):
        def e(self, *arg, **kwarg):
            self.runtime.data['where'].append(
                self.bridge == self.bridge.point_to
            )
            return func(self, *arg, **kwarg)
        return e

    @brigde_wrapper
    def select(self, *lst):
        return super(JoinModel, self).select(*lst)

    @brigde_wrapper
    def update(self, *lst):
        return super(JoinModel, self).update(*lst)

    @brigde_wrapper
    def delete(self, target_model=None):
        return super(JoinModel, self).delete(target_model)
