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

__version__ = '0.2.5'


import sys
from types import ModuleType

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

# marks for query types
QUERY_INSERT = 20
QUERY_UPDATE = 21
QUERY_SELECT = 22
QUERY_DELETE = 23


# exceptions

class CURDException(Exception):
    """There was an ambiguous exception occurred"""
    pass


class ForeignKeyNotFound(Exception):
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
        e.g. User.id._in(1, 2, 3, 4, 5)
        """
        return Expr(self, values, OP_IN)


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

    expr_cache = {}  # dict to cache parsed expr

    @staticmethod
    def __parse_expr_one_side(side):

        if isinstance(side, Field):
            return side.fullname
        elif isinstance(side, Expr):
            return Compiler.parse_expr(side)
        else:  # string or number
            escaped_str = MySQLdb.escape_string(str(side))  # !safety
            return (
                # if basestring(str or unicode..),  wrap it with quote
                "'" + escaped_str + "'" if isinstance(side, basestring) else escaped_str
            )

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
        elif op is OP_IN:
            values_str = ', '.join(tostr(value) for value in r)
            string = tostr(l) + ' in ' + '(' + values_str + ')'

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

        if query_type is QUERY_INSERT:
            SQL = 'insert into ' + target_table + _set
        elif query_type is QUERY_UPDATE:
            SQL = 'update ' + target_table + _set + _where
        elif query_type is QUERY_SELECT:
            SQL = 'select ' + _select + ' from ' + from_table + _where + _orderby
        elif query_type is QUERY_DELETE:
            SQL = 'delete ' + target_table + ' from ' + from_table + _where

        return SQL


class Runtime(object):
    """Runtime information manager"""

    def __init__(self, model=None):
        self.model = model
        self.data = {}.fromkeys(('where', 'set', 'orderby', 'select'), None)
        # reset runtime data
        self.reset_data()

    def reset_data(self):
        '''reset runtime data'''
        dct = dict((key, []) for key in self.data.keys())
        self.data.update(dct)

    def set_orderby(self, field_desc):
        '''
        filed_desc
          tuple, tuple of (field, desc), desc is a boolean
        '''
        self.data['orderby'] = list(field_desc)

    def set_select(self, fields):
        flst = list(fields)
        primarykey = self.model.primarykey

        if flst:
            # add primarykey(s) to select fields list
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

    def Q(QUERY_TYPE):
        @staticmethod
        def _Q(runtime, target_model=None):
            sql = Compiler.gen_sql(runtime, QUERY_TYPE, target_model)
            cursor = Database.execute(sql)

            if QUERY_TYPE is QUERY_INSERT:
                re = cursor.lastrowid if cursor.rowcount else None
            elif QUERY_TYPE in (QUERY_UPDATE, QUERY_DELETE):
                re = cursor.rowcount
            elif QUERY_TYPE is QUERY_SELECT:
                re = SelectResult(cursor, runtime.model, runtime.data['select'])

            if QUERY_TYPE is not QUERY_SELECT:  # close cursor on non-select query
                cursor.close()
            # dont forget clear runtime infomation after query
            runtime.reset_data()
            return re
        return _Q

    insert = Q(QUERY_INSERT)

    delete = Q(QUERY_DELETE)

    update = Q(QUERY_UPDATE)

    select = Q(QUERY_SELECT)


class SelectResult(object):

    def __init__(self, cursor, model, fields):
        self.model = model
        self.fields = fields  # fields select out
        self.cursor = cursor

        # field name dont duplicate:
        # if `user.name`, `post.name` both in the field list, return data dict
        # keys will contain `user.name` and `post.name` both, but if `user.name`
        # in field list and `post.name` doesn't, the returned data dict keys
        # will only contain the key `name`
        # so, this attribute `nfdct` makes a dict {field name: field object}
        # responsing to MySQLdb's behavior

        nfdct = {}

        for field in self.fields:
            if field.name not in nfdct:
                nfdct[field.name] = field
            else:
                nfdct[field.fullname] = field

        self.nfdct = nfdct

    def mddct(self, data):  # {model: data dict}
        models = self.model.models
        b = dict((m, {}) for m in models)

        for field_name, value in data.iteritems():
            field = self.nfdct[field_name]
            data_dct = b[field.model]
            data_dct[field.name] = value
        return b

    def fetchone(self):  # fetch one row each time
        '''Fetch a single row each time'''
        dct = self.cursor.fetchone()

        if self.model.single:
            return self.model(**dct) if dct else None
        else:
            b = self.mddct(dct)
            return tuple(m(**b[m]) for m in self.model.models)

    def fetchall(self):
        '''Fetch all rows at a time'''
        data = self.cursor.fetchall()

        if self.model.single:
            for dct in data:
                yield self.model(**dct)
        else:
            for dct in data:
                b = self.mddct(dct)
                yield tuple(m(**b[m]) for m in self.model.models)

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
        # update data dict from data parameter
        self.data.update(dct)
        # cache for data
        self._cache = self.data.copy()

    @classmethod
    def get_fields(cls):
        """return list of this model's fields"""
        return cls.fields.values()

    @classmethod
    def select(cls, *flst):
        """
        parameters:
          flst, list of fields to select out
        e.g.
          User.select(User.name, User.email)
        """
        cls.runtime.set_select(flst)
        return Query.select(cls.runtime)

    @classmethod
    def where(cls, *lst, **dct):
        """
        parameters:
          lst, expressions, e.g.: User.id > 3
          dct, datas, e.g.: name="Join"

        e.g.
          User.where(User.name == "Join", id=4).select()
          =>
          select user.id, user.email, user.name from user where user.name = 'Join' and user.id = 4
        """
        cls.runtime.set_where(lst, dct)
        return cls

    @classmethod
    def update(cls, *lst, **dct):
        """
        parameter:
          lst, expressions, e.g. User.name == "Join"
          dct, datas, e.g. name="Join"

        e.g.
          User.where(User.id <=5 ).update(name="Join")
          =>
          update user set user.name = 'Join' where user.id <= 5
        """
        cls.runtime.set_set(lst, dct)
        return Query.update(cls.runtime)

    @classmethod
    def orderby(cls, field, desc=False):
        """
        parameter:
          field, field to order by
          desc, if desc, bool
        e.g.
          User.where(User.id <= 5).orderby(User.id, desc=True).select()
        """
        cls.runtime.set_orderby((field, desc))
        return cls

    @classmethod
    def at(cls, _id):
        """
        at(_id) is the alias of where(Model.primarykey == _id)
        """
        return cls.where(cls.primarykey == _id)

    @classmethod
    def create(cls, *lst, **dct):
        """
        parameters:
          lst, expressions, e.g. User.name == "xiaoming"
          dct, e.g. name="xiaoming"

        e.g.
          User.create(name="Join", email="Join@gmail.com")
          =>
          insert into user set user.name = 'Join', user.email = 'Join@gmail.com'
        """
        cls.runtime.set_set(lst, dct)
        _id = Query.insert(cls.runtime)

        if _id is not None:
            dct[cls.primarykey.name] = _id  # add id to dct
            return cls(*lst, **dct)

        return None

    @classmethod
    def delete(cls):
        """
        e.g.
          User.at(1).delete()
          =>
          delete user from user where user.id = 1
        """
        return Query.delete(cls.runtime)

    @property
    def _id(self): # value of primarykey
        """value of this instance's primarykey"""
        cls = self.__class__
        return self.data.get(cls.primarykey.name, None)

    def save(self):
        """save this instance's data to database"""
        model = self.__class__
        _id = self._id

        if not _id:  # if insert
            model.runtime.set_set([], self.data)
            ret = Query.insert(model.runtime)

            if ret is not None:
                self.data[model.primarykey.name] = ret  # set primarykey value
                self._cache = self.data.copy()  # sync cache after save
        else:  # else, update
            # only update changed data
            dct = dict(set(self.data.items()) - set(self._cache.items()))

            if not dct:
                return 0  # data not change

            ret = model.at(_id).update(**dct)
            self._cache = self.data.copy()  # sync cache after save
        return ret

    def destroy(self):
        """delete this object's data in database"""
        if self._id:
            model = self.__class__
            return model.at(self._id).delete()


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
        self.runtime.set_select(lst)
        return Query.select(self.runtime)

    def update(self, *lst):
        self.runtime.set_set(lst, {})
        return Query.update(self.runtime)

    def delete(self, target_model=None):
        return Query.delete(self.runtime, target_model=target_model)

    def orderby(self, field, desc=False):
        self.runtime.set_orderby((field, desc))
        return self


class JoinModel(Models):
    """
    JoinModel(main_model, join_model)
    e.g. Post & User will get JoinModel(Post, User)
    """

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
    def update(self, *lst):
        return super(JoinModel, self).update(*lst)

    @brigde_wrapper
    def delete(self, target_model=None):
        return super(JoinModel, self).delete(target_model)


#
# Sugar Part - Syntactic_sugar.
#
# Use Mix-in to add new and cool features to CURD.py
# Enable Sugar: from CURD import Sugar
#
# Sugars are written in method loadSugar

def loadSugar():

    # -------------------------------------- {
    # Model[index]
    # e.g. user = User[2]

    MetaModel.__getitem__ = (
        lambda model, index: model.at(index).select().fetchone()
    )
    # -------------------------------------- }

    # -------------------------------------- {
    def MetaModel_getslice(model, start, end):
        # model[start, end]
        # e.g. users = User[1:3]
        # Produce: select * from user where user.id >= start and user.id <= end
        exprs = []

        if start:
            exprs.append(model.primarykey >= start)

        if end < 0x7fffffff: # extremely big..
            exprs.append(model.primarykey <= end)

        return model.where(*exprs).select().fetchall()

    MetaModel.__getslice__ = MetaModel_getslice
    # --------------------------------------- }

    # --------------------------------------- {
    # object in model
    # e.g. user in User
    # return True or False
    def MetaModel_contains(model, obj):
        if isinstance(obj, model) and model.where(**obj.data).select().count:
            return True
        return False
    MetaModel.__contains__ = MetaModel_contains
    # --------------------------------------- }


# module wrapper for sugar
class ModuleWrapper(ModuleType):

    def __init__(self, module):
        #
        # I hate this way to wrap module, auctually i just need
        # some way like this:
        # from CURD import Sugar
        # this line(above) will run some code
        #
        self.module = module

    def __getattr__(self, name):

        try:
            return getattr(self.module, name)
        except:
            if name == "Sugar":
                loadSugar()
                return
            raise AttributeError


sys.modules[__name__] = ModuleWrapper(sys.modules[__name__])
