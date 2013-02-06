# coding=utf-8
#
# __     ___       ____
# \ \   / (_)_ __ / ___| ___
#  \ \ / /| | '__| |  _ / _ \
#   \ V / | | |  | |_| | (_) |
#    \_/  |_|_|   \____|\___/
#
#   Tiny Python ORM for MySQL
#
#   E-mail : nz2324@126.com
#
#   URL : https://virgo.readthedocs.org/
#
#   Licence : BSD
#
#
# Permission to use, copy, modify,
# and distribute this software for any purpose with
# or without fee is hereby granted,
# provided that the above copyright notice
# and this permission notice appear in all copies.
#

import re
import MySQLdb
import MySQLdb.cursors


# regular expression to get matched rows number from cursor's info
VG_RowsMatchedRe = re.compile(r'Rows matched: (\d+)')


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


class Database(object):
    """Manage Database connection"""

    # configs for connection with default value
    configs = {
        "host": "localhost",
        "port": 3306,
        "db": "",
        "user": "",
        "passwd": "",
        "charset": "utf8"
    }

    # debuge mode?
    debug = True

    # It is strongly recommended that you set this True
    autocommit = True

    # MySQL connection object, you should use method get_conn to get it
    conn = None

    # record query times
    query_times = 0

    # record SQL last time executed
    SQL = None

    @classmethod
    def config(cls, debug=True, autocommit=True, **configs):
        """
        Configure the database connection.

        The connection will be auto established with these configs.

        Keyword parameters for this method:

          host
            string, host to connect

          user
            string, user to connect as

          passwd
            string, password to use

          db
            string, database to use

          port
            integer, TCP/IP port to connect to

          charset
            string, charset of connection

        See the MySQLdb documentation for more infomation,
        the parameters of MySQLdb.connect are all supported.
        """
        cls.configs.update(configs)
        cls.debug = debug
        cls.autocommit = autocommit

    @classmethod
    def connect(cls):
        """
        Connect to database, singleton pattern.
        This will new one conn object.
        """
        cls.conn = MySQLdb.connect(
            cursorclass=MySQLdb.cursors.DictCursor,
            **cls.configs
        )
        cls.conn.autocommit(cls.autocommit)

    @classmethod
    def get_conn(cls):
        """
        Get MySQL connection object.
        if the conn is open and working, return it,
        else, new one and return it.
        """
        # singleton
        if not cls.conn or not cls.conn.open:
            cls.connect()

        try:
            cls.conn.ping()  # ping to test if the connection is working
        except MySQLdb.OperationalError:
            cls.connect()

        return cls.conn

    @classmethod
    def execute(cls, SQL):
        """
        Execute one SQL command.

        Parameter:
          SQL
            string, SQL command to run.
        """
        cursor = cls.get_conn().cursor()

        try:
            cursor.execute(SQL)
        except Exception, e:
            if cls.debug:  # if debug, report the SQL
                print "SQL:", SQL
            raise e

        cls.query_times += 1
        cls.SQL = SQL

        # add attribute 'matchedRows' to cursor.store query matched rows number
        cursor.matchedRows = int(
            VG_RowsMatchedRe.search(cursor._info).group(1)
        ) if cursor._info else int(cursor.rowcount)

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


# descriptor for Field objects
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

    Field examples: User.name, User.age ..
    """

    def __init__(self, is_primarykey=False, is_foreignkey=False):
        self.is_primarykey = is_primarykey
        self.is_foreignkey = is_foreignkey

    # describe model's attr
    def describe(self, name, model):
        self.name = name
        self.model = model
        # fullname e.g. : User.id 's fullname is "user.id"
        self.fullname = self.model.table_name + "." + self.name
        # describe the attribute, reload its access control of writing, reading
        setattr(model, name, FieldDescriptor(self))

    def like(self, pattern):
        """
        e.g. User.name.like("Amy%")
        """
        return Expr(self, pattern, OP_LIKE)

    def between(self, value1, value2):
        """
        e.g. User.id.bettwen(3, 7)
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
    """
    Compile expressions and sequence of methods to SQL string(s).
    """

    # operator mapping
    OP_MAPPING = {
        OP_LT: " < ",
        OP_LE: " <= ",
        OP_GT: " > ",
        OP_GE: " >= ",
        OP_EQ: " = ",
        OP_NE: " <> ",
        OP_ADD: " + ",
        OP_AND: " and ",
        OP_OR: " or ",
        OP_LIKE: "like"
    }

    expr_cache = {}  # dict to store parsed expressions {expr: string}

    # parse one side of expression to string
    @staticmethod
    def __parse_expr_one_side(side):

        if isinstance(side, Field):
            return side.fullname
        elif isinstance(side, Expr):
            return Compiler.parse_expr(side)
        else:  # string or numbers
            escapestr = MySQLdb.escape_string(str(side))
            return (
                "'" + escapestr + "'" if isinstance(side, str) else escapestr
            )

    # parse expressions to string
    @staticmethod
    def parse_expr(expr):

        # first check cache
        cache = Compiler.expr_cache
        if expr in cache:
            return cache[expr]

        l, op, r = expr.left, expr.op, expr.right

        OP_MAPPING = Compiler.OP_MAPPING

        string = None

        tostr = Compiler.__parse_expr_one_side

        if op in OP_MAPPING:
            string = tostr(l) + OP_MAPPING[op] + tostr(r)
        elif op is OP_BETWEEN:
            string = (
                tostr(l) + " between " + tostr(r[0]) + " and " + tostr(r[1])
            )
        elif op is OP_IN:
            valuestr = ", ".join(tostr(value) for value in r)
            string = (
                tostr(l) + " in " + "(" + valuestr + ")"
            )

        # dont forget to set cache
        cache[expr] = string
        return string


class Runtime(object):
    """
    Runtime infomation manager
    """

    def __init__(self, model=None):
        self.model = model

        self.data = {}.fromkeys((
            "where", "set", "orderby", "select"
        ), None)

        # reset runtime data
        self.reset_data()

    # reset runtime data
    def reset_data(self):
        dct = dict((i, []) for i in self.data.keys())
        self.data.update(dct)

    def set_orderby(self, field_desc_tuple):
        # field_desc_tuple, (field, bool)
        self.data['orderby'] = list(field_desc_tuple)

    def set_select(self, fields):
        flst = list(fields)
        primarykey = self.model.primarykey

        if flst:
            if self.model.single:  # if single model
                flst.append(primarykey)  # add primarykey to select fields
            else:
                flst.extend(primarykey)  # extend primarykeys
        else:
            flst = self.model.get_fields()

        # remove duplicates
        self.data['select'] = list(set(flst))

    def set_where(self, lst, dct):
        lst = list(lst)

        # if single model, turn dct to expressions
        if self.model.single:
            fields = self.model.fields
            lst.extend(
                [fields[k] == v for k, v in dct.iteritems()]
            )

        self.data['where'] = lst

    def set_set(self, lst, dct):
        lst = list(lst)  # cast to list, we need to append xxx to it

        if self.model.single:
            fields = self.model.fields
            primarykey = self.model.primarykey

            for k, v in dct.iteritems():
                if fields[k] is not primarykey:
                    lst.append(fields[k] == v)

        self.data['set'] = lst


class MetaModel(type):  # metaclass for 'single Model'

    def __init__(cls, name, bases, attrs):

        # use lowercase of clsname as table name
        cls.table_name = cls.__name__.lower()
        # {field name: filed}
        fields = {}
        # PrimaryKey object
        primarykey = None

        # foreach filed, describe it and find the primarykey
        for name, attr in cls.__dict__.iteritems():
            if isinstance(attr, Field):
                attr.describe(name, cls)
                fields[name] = attr
                if attr.is_primarykey:
                    primarykey = attr

        if primarykey is None:  # if primarykey not found
            primarykey = PrimaryKey()  # then we new one primarykey: 'id'
            primarykey.describe("id", cls)
            fields['id'] = primarykey

        cls.fields = fields
        cls.primarykey = primarykey
        cls.runtime = Runtime(cls)


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
    single = True  # mark if single model

    def __init__(self, *lst, **dct):
        self.data = {}
        # update data dict from expressions
        for expr in lst:
            field, value = expr.left, expr.right
            self.data[field.name] = value
        # update data dict from data parameter
        self.data.update(dct)

    @classmethod
    def get_fields(cls):
        """
        return list of this model's fields
        """
        return cls.fields.values()

    @classmethod
    def select(cls, *flst):
        """
        Parameters:
          flst, fields
        e.g.
          User.select(User.name, User.email)
        """
        cls.runtime.set_select(flst)
        # TODO: return query result
        return cls

    @classmethod
    def where(cls, *lst, **dct):
        """
        Parameters:
          lst, expressions, e.g.: User.id > 3
          dct, datas, e.g.: name = "Join"
        e.g.
          User.where(User.name == "Join", id=4).select()
        """
        cls.runtime.set_where(lst, dct)
        return cls

    @classmethod
    def update(cls, *lst, **dct):
        cls.runtime.set_set(lst, dct)
        # TODO: return update result
