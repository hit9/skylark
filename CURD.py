# coding=utf8
#  ____ _   _ ____  ____
# / ___| | | |  _ \|  _ \  _ __  _   _
#| |   | | | | |_) | | | || '_ \| | | |
#| |___| |_| |  _ <| |_| || |_) | |_| |
# \____|\___/|_| \_\____(_) .__/ \__, |
#                         |_|    |___/
#
#   Tiny Python ORM for MySQL
#
#   E-mail: nz2324@126.com
#
#   URL: https://github.com/hit9/CURD.py
#
#   License: BSD
#
#
# Permission to use, copy, modify,
# and distribute this software for any purpose with
# or without fee is hereby granted,
# provided that the above copyright notice
# and this permission notice appear in all copies.
#

__version__ = '0.3.2'


import MySQLdb
import MySQLdb.cursors

# marks for operators
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

# marks for query types
QUERY_INSERT = 20
QUERY_UPDATE = 21
QUERY_SELECT = 22
QUERY_DELETE = 23

# supported sql functions
# aggregate functions
FUNC_COUNT = 31
FUNC_SUM = 32
FUNC_MAX = 33
FUNC_MIN = 34
FUNC_AVG = 35
# scalar functions
FUNC_UCASE = 41
FUNC_LCASE = 42

# CURD.py FLAGS
DATA_ENCODING = 'utf8'  # your python code encoding


# exceptions

class CURDException(Exception):
    """There was an ambiguous exception occurred"""
    pass


class ForeignKeyNotFound(CURDException):
    """Foreign key not found in main model"""
    pass


class Database(object):
    """Database connection manager"""

    # configuration for connection with default values
    configs = {
        'host': 'localhost',
        'port': 3306,
        'db': '',
        'user': '',
        'passwd': '',
        'charset': 'utf8'
    }

    # It is strongly recommended that you set this True
    autocommit = True

    # MySQL connection object
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

    @classmethod
    def connect(cls):
        """
        Connect to database, this method will new a connect object
        """
        cls.conn = MySQLdb.connect(
            cursorclass=MySQLdb.cursors.DictCursor, **cls.configs
        )
        cls.conn.autocommit(cls.autocommit)

    @classmethod
    def get_conn(cls):
        """
        Get MySQL connection object.

        if the conn is open and working
          return it.
        else
          new another one and return it.
        """

        # singleton
        if not cls.conn or not cls.conn.open:
            cls.connect()

        try:
            # ping to test if this conn is working
            cls.conn.ping()
        except MySQLdb.OperationalError:
            cls.connect()

        return cls.conn

    @classmethod
    def execute(cls, sql):
        """
        Execute one sql

        parameters
          sql
            string, sql command to run
        """
        cursor = cls.get_conn().cursor()
        cursor.execute(sql)
        return cursor


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
    """
    Expression object.

    You need't new an expression in this way: myexpr = Expr(left, right, op)

    Use expression like this:
      User.id == 4
      User.name == "Amy"
    """

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
    """
    Field object.

    examples: User.name, User.age ..
    """

    def __init__(self, is_primarykey=False, is_foreignkey=False):
        self.is_primarykey = is_primarykey
        self.is_foreignkey = is_foreignkey

    def describe(self, name, model):
        self.name = name
        self.model = model
        # `fullname`: e.g.: User.id => fullname is 'user.id'
        self.fullname = self.model.table_name + '.' + self.name
        # describe the attribute
        setattr(model, name, FieldDescriptor(self))

    def like(self, pattern):
        """
        e.g. User.name.like("Amy%")
        """
        return Expr(self, pattern, OP_LIKE)

    def between(self, value1, value2):
        """
        e.g. User.id.between(3, 7)
        """
        return Expr(self, (value1, value2), OP_BETWEEN)

    def _in(self, *values):
        """
        e.g.:
          User.id._in(1, 2, 3, 4, 5)
          User.id._in(Post.select(Post.user_id))
        """
        return Expr(self, values, OP_IN)

    def not_in(self, *values):
        """
        e.g.:
          User.id.not_in(1, 2, 3, 4, 5)
          User.id.not_in(Post.select(Post.user_id))
        """
        return Expr(self, values, OP_NOT_IN)


class PrimaryKey(Field):
    """
    PrimaryKey object.

    PrimaryKey example: User.id
    """

    def __init__(self):
        super(PrimaryKey, self).__init__(is_primarykey=True)


class ForeignKey(Field):
    """
    ForeignKey object.
    ForeignKey example: Post.user_id = ForeignKey(point_to=User.id)

    Parameter:
      point_to
        PrimaryKey object, the primary key this foreignkey referenced to.
    """

    def __init__(self, point_to):
        super(ForeignKey, self).__init__(is_foreignkey=True)
        self.point_to = point_to


class Function(object):
    """
    Function object. e.g. `count`, `max`, `sum` in SQL
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
        return '<Function %r>' % self.fullname


class Fn(object):

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
        QUERY_SELECT: 'select {select} from {from}{where}{orderby}{limit}',
        QUERY_DELETE: 'delete {target} from {from}{where}'
    }

    expr_cache = {}  # dict to cache parsed expr

    @staticmethod
    def __parse_expr_one_side(side):

        if isinstance(side, (Field, Function)):  # field
            return side.fullname
        elif isinstance(side, Expr):  # expressions
            return Compiler.parse_expr(side)
        elif isinstance(side, Query):  # sub query
            return side.sql
        elif isinstance(side, unicode):  # encode it
            side = side.encode(DATA_ENCODING)
            return Compiler.__parse_expr_one_side(side)
        else:  # use MySQLdb's `string_literal` to format Python
               # objects to SQL string literal
            return Database.get_conn().string_literal(side)

    @staticmethod
    def parse_expr(expr):
        '''parse expression to string'''

        cache = Compiler.expr_cache

        # check cache at first
        if expr in cache:  # `in` statement use `__hash__` and then `__eq__`
            return cache[expr]

        # make alias
        l, op, r = expr.left, expr.op, expr.right
        OP_MAPPING = Compiler.OP_MAPPING
        tostr = Compiler.__parse_expr_one_side

        string = None

        if op in OP_MAPPING:
            string = tostr(l) + OP_MAPPING[op] + tostr(r)
        elif op is OP_BETWEEN:
            string = tostr(l) + ' between ' + tostr(r[0]) + ' and ' + tostr(r[1])
        elif op in (OP_IN, OP_NOT_IN):
            values_str = ', '.join(tostr(value) for value in r)
            string = (tostr(l) + '%s in (' + values_str + ')') % (
                ' not' if op is OP_NOT_IN else '')


        # set cache
        cache[expr] = string

        return string

    # ------------------ runtime part -----

    @staticmethod
    def parse_orderby(lst):
        '''parse orderby tuple to string'''
        if not lst:  # empty list
            return ''

        orderby_str = ' order by ' + lst[0].fullname

        if lst[1]:
            orderby_str += ' desc '

        return orderby_str

    @staticmethod
    def parse_where(lst):
        '''parse where expressions to string'''
        if not lst:
            return ''
        return ' where ' + ' and '.join(
            Compiler.parse_expr(expr) for expr in lst)

    @staticmethod
    def parse_select(lst):
        '''parse select fields to string'''
        return ', '.join(field.fullname for field in lst)

    @staticmethod
    def parse_limit(lst):
        if not lst:
            return ''

        offset, rows = lst

        if offset is None:
            return ' limit %s ' % rows
        else:
            return ' limit %s, %s ' % (offset, rows)

    @staticmethod
    def parse_set(lst):
        '''parse set expressions to string'''
        return ' set ' + ', '.join(
            Compiler.parse_expr(expr) for expr in lst
        )

    @staticmethod
    def gen_sql(runtime, query_type, target_model=None):
        '''
        Generate SQL from runtime information.

        parameters:

          runtime
            Runtime, runtime instance

          query_type
            macros, query_types, the QUERY_**:

          target_model
            Model, model to delete, update, select or insert
        '''

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

        pattern = Compiler.SQL_PATTERNS[query_type]

        SQL = pattern.format(**{
            'target': target_table,
            'set': _set,
            'from': from_table,
            'where': _where,
            'select': _select,
            'limit': _limit,
            'orderby': _orderby
        })

        return SQL


class Runtime(object):
    """Runtime information manager"""

    def __init__(self, model=None):
        self.model = model
        self.data = {}.fromkeys(('where', 'set', 'orderby', 'select', 'limit'), None)
        # reset runtime data
        self.reset_data()

    def reset_data(self):
        '''reset runtime data'''
        dct = dict((key, []) for key in self.data.keys())
        self.data.update(dct)

    def __repr__(self):
        return '''<Runtime %r>''' % self.data

    def set_orderby(self, field_desc):
        '''
        filed_desc
          tuple, tuple of (field, desc), desc is a boolean
        '''
        self.data['orderby'] = list(field_desc)

    def set_limit(self, offset_rows):
        self.data['limit'] = list(offset_rows)

    def set_select(self, fields, auto_append_primarykey=True):
        flst = list(fields)
        primarykey = self.model.primarykey

        if flst:
            if auto_append_primarykey:
                if self.model.single:
                    flst.append(primarykey)
                else:
                    flst.extend(primarykey)
        else:
            # else, empty args -> select all fields
            flst = self.model.get_fields()
        # remove duplicates
        self.data['select'] = list(set(flst))

    def set_where(self, lst, dct):
        # lst: list of expressions, dct: dict if {filed=>value}
        lst = list(lst)

        # turn dct to list of expressions
        if self.model.single:  # muti models cannt use dct arg
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


class Query(object):

    def __init__(self, query_type, runtime, target_model=None):
        self.query_type = query_type
        self.sql = Compiler.gen_sql(runtime, self.query_type, target_model)
        runtime.reset_data()  # ! important: clean runtime right on this query initialized

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
        self.select_fields = runtime.data['select']
        super(SelectQuery, self).__init__(QUERY_SELECT, runtime, target_model)

    def __iter__(self):
        result = self.execute()
        return result.fetchall()

    def execute(self):
        cursor = Database.execute(self.sql)
        return SelectResult(cursor, self.from_model, self.select_fields)

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

        self.ntof = {}

    def format(self, data):
        if self.model.single:
            # function's fullname in data to name
            for f in self.flst:
                if isinstance(f, Function):
                    data[f.name] = data.pop(f.fullname)
            return data
        else:
            ntof = self.ntof
            if not ntof:  # initialize ntof once
                for f in self.flst:
                    if isinstance(f, Field):
                        if f.name not in ntof:
                            ntof[f.name] = f
                        else:
                            ntof[f.fullname] = f
                    elif isinstance(f, Function):
                        ntof[f.fullname] = f

            dct = dict((m, {}) for m in self.model.models)

            for key, value in data.iteritems():
                f = ntof[key]
                data_dct = dct[f.model]
                data_dct[f.name] = value

            return dct

    def __instance_from_db(self, model, data):
        instance = model()
        instance.set_in_db(True)
        # set functions as attributes
        for func in self.flst:
            if isinstance(func, Function) and func.model is model:
                setattr(instance, func.name, data.pop(func.name))
        instance.data.update(data)
        return instance

    def fetchone(self):
        '''Fetch a single row each time'''
        data = self.cursor.fetchone()

        if data is None:
            return None

        if self.model.single:
            return self.__instance_from_db(self.model,
                                               self.format(data))
        else:
            dct = self.format(data)
            return tuple(self.__instance_from_db(m, dct[m]) for m in self.model.models)

    def fetchall(self):
        '''Fetch all rows at a time'''
        rows = self.cursor.fetchall()

        if self.model.single:
            for data in rows:
                yield self.__instance_from_db(self.model, self.format(data))
        else:
            for data in rows:
                dct = self.format(data)
                yield tuple(self.__instance_from_db(m, dct[m]) for m in self.model.models)

    @property
    def count(self):
        return self.cursor.rowcount


class MetaModel(type):  # metaclass for `Model`

    def __init__(cls, name, bases, attrs):

        cls.table_name = cls.__name__.lower()  # clsname lowercase => table name

        fields = {}  # {field_name: field}
        primarykey = None

        # foreach field, describe it and find the primarykey
        for name, attr in cls.__dict__.iteritems():
            if isinstance(attr, Field):
                attr.describe(name, cls)
                fields[name] = attr
                if attr.is_primarykey:
                    primarykey = attr

        if primarykey is None:  # if primarykey not found
            primarykey = PrimaryKey()  # use `id` as default
            primarykey.describe('id', cls)
            fields['id'] = primarykey

        cls.fields = fields
        cls.primarykey = primarykey
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
    """
    Model object. Tables are mapped to models.

    Parameters:

      expressions
        Expr objects, e.g. User(User.name == "Join")

      datas
        e.g. User(name="Join")

    """

    __metaclass__ = MetaModel

    single = True  # single model

    def __init__(self, *lst, **dct):
        self.data = {}
        # update data dict from expressions
        for expr in lst:
            field, value = expr.left, expr.right
            self.data[field.name] = value

        self.data.update(dct) # update data dict from data parameter
        self._cache = self.data.copy()  # cache for data
        self.set_in_db(False)  # not in database

    @classmethod
    def get_fields(cls):
        """return list of this model's fields"""
        return cls.fields.values()

    @classmethod
    def insert(cls, *lst, **dct):
        cls.runtime.set_set(lst, dct)
        return InsertQuery(cls.runtime)

    @classmethod
    def select(cls, *flst):
        cls.runtime.set_select(flst, auto_append_primarykey=True)
        return SelectQuery(cls.runtime)

    @classmethod
    def select_without_primarykey(cls, *flst):
        cls.runtime.set_select(flst, auto_append_primarykey=False)
        return SelectQuery(cls.runtime)

    @classmethod
    def where(cls, *lst, **dct):
        cls.runtime.set_where(lst, dct)
        return cls

    @classmethod
    def update(cls, *lst, **dct):
        cls.runtime.set_set(lst, dct)
        return UpdateQuery(cls.runtime)

    @classmethod
    def orderby(cls, field, desc=False):
        cls.runtime.set_orderby((field, desc))
        return cls

    @classmethod
    def limit(cls, rows, offset=None):
        cls.runtime.set_limit((offset, rows))
        return cls

    @classmethod
    def at(cls, _id):  # TODO: changed to limit
        return cls.where(cls.primarykey == _id)

    @classmethod
    def create(cls, *lst, **dct):
        query = cls.insert(*lst, **dct)
        id = query.execute()
        if id is not None:
            dct[cls.primarykey.name] = id  # add id to dct
            instance = cls(*lst, **dct)
            instance.set_in_db(True)
            return instance

    @classmethod
    def delete(cls):
        return DeleteQuery(cls.runtime)

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
    def _id(self):  # value of primarykey
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

            if dct:
                query = model.at(self._id).update(**dct)
                rows_affected = query.execute()
            else:
                rows_affected = 0L
            self._cache = self.data.copy()  # sync cache after saving
            return rows_affected

    def destroy(self):
        if self._in_db:
            return type(self).at(self._id).delete().execute()
        # TODO:need raise an exception?

    # SQL Function shortcuts
    def fn(func_type):
        @classmethod
        def _fn(cls, field=None):
            if field is None:
                field = cls.primarykey
            func = Function(field, func_type)
            query = cls.select_without_primarykey(func)
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
    """Mutiple models"""

    def __init__(self, *models):

        self.models = list(models)  # cast to list
        self.single = False
        self.runtime = Runtime(self)
        self.table_name = ", ".join([m.table_name for m in self.models])
        self.primarykey = [m.primarykey for m in self.models]

    def get_fields(self):
        lst = [m.get_fields() for m in self.models]
        return sum(lst, [])

    def where(self, *lst):
        self.runtime.set_where(lst, {})
        return self

    def select(self, *lst):
        self.runtime.set_select(lst, auto_append_primarykey=True)
        return SelectQuery(self.runtime)

    def select_without_primarykey(self, *flst):
        self.runtime.set_select(flst, auto_append_primarykey=False)
        return SelectQuery(self.runtime)

    def update(self, *lst):
        self.runtime.set_set(lst, {})
        return UpdateQuery(self.runtime)

    def delete(self, target_model=None):
        return DeleteQuery(self.runtime, target_model=target_model)

    def orderby(self, field, desc=False):
        self.runtime.set_orderby((field, desc))
        return self

    def limit(self, rows, offset=None):
        self.runtime.set_limit((offset, rows))
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

    def __init__(self, main, join):  # main's foreignkey is join's primarykey
        super(JoinModel, self).__init__(main, join)

        self.bridge = None # the foreignkey point to join

        # try to find the foreignkey
        for field in main.get_fields():
            if field.is_foreignkey and field.point_to is join.primarykey:
                self.bridge = field

        if not self.bridge:
            raise ForeignKeyNotFound(
                "Foreign key references to "
                "'%s' not found in '%s'" % (join.__name__, main.__name__))

    def brigde_wrapper(func):
        def e(self, *arg, **kwarg):
            # build brigde
            self.runtime.data['where'].append(
                self.bridge == self.bridge.point_to
            )
            return func(self, *arg, **kwarg)
        return e

    @brigde_wrapper
    def select(self, *lst):
        return super(JoinModel, self).select(*lst)

    @brigde_wrapper
    def select_without_primarykey(self, *lst):
        return super(JoinModel, self).select_without_primarykey(*lst)

    @brigde_wrapper
    def update(self, *lst):
        return super(JoinModel, self).update(*lst)

    @brigde_wrapper
    def delete(self, target_model=None):
        return super(JoinModel, self).delete(target_model)
