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


class Expr(object):
    """
    Expression object.

    You need't new an expression in this way: myexpr = Expr(left, right, op)

    Use expression like this:
      User.id == 4
      User.name == "Amy"

    API here:
      tostr()  turn this expression to string
    """

    def __init__(self, left, right, op):
        self.left = left
        self.right = right
        self.op = op
        self.__str = None  # private var, store expression-string once tostr called

    def __tostr(self, side):  # private method to turn one side to string
        if isinstance(side, Field):
            return side.fullname
        elif isinstance(side, Expr):
            return side.tostr()
        else:  # string or number
            return "'" + MySQLdb.escape_string(str(side)) + "'"   # escape_string

    def tostr(self):
        """
        Turn expression object into string.
          eg.
            User.id < 6   =>  "user.id < 6"
        """
        pass


class Field(object):
    pass
