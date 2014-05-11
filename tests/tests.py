# coding=utf8
#
# How to Run tests:
# Requirements:
#    pip install toml.py
#    pip install pymysql
#    pip install MySQL-python
#    pip install psycopg2
#
# ./runtests.sh


import os
import sys
import logging
logging.basicConfig(level=logging.INFO)

import toml

sys.path.insert(0, '..')
from skylark import Database, database, DBAPI_MAPPINGS, DatabaseType

dbapi_name = os.environ.get('DBAPI', 'MySQLdb')
dbapi = __import__(dbapi_name)
configs = toml.loads(open('conf.toml').read())[dbapi_name]

db_type_mappings = {
    'pymysql': 'mysql',
    'MySQLdb': 'mysql',
    'sqlite3': 'sqlite',
    'psycopg2': 'postgres'
}

db_type = db_type_mappings[dbapi_name]

user_sql = open('%s.user.sql' % db_type).read()
post_sql = open('%s.post.sql' % db_type).read()

db = DatabaseType()
db.set_dbapi(dbapi)
db.config(**configs)


class Test(object):

    def setUp(self):
        db.execute(user_sql)
        db.execute(post_sql)

    def tearDown(self):
        db.execute("drop table t_post")
        db.execute("drop table t_user")


class TestDatabase_:

    def test_alias(self):
        assert database is Database

    def __shouldnt_import(self, name):
        try:
            __import__(name)
            raise Exception
        except ImportError:
            pass

    def test_init(self):
        assert database.conn is None
        assert database.configs == {}
        assert database.dbapi.module.__name__ in DBAPI_MAPPINGS

        # test load orders
        name = database.dbapi.module.__name__

        if name == 'MySQLdb':
            assert __import__('MySQLdb')
        elif name == 'pymysql':
            assert __import__('pymysql')
            self.__shouldnt_import('MySQLdb')
        elif name == 'psycopg2':
            assert __import__('psycopg2')
            self.__shouldnt_import('MySQLdb')
            self.__shouldnt_import('pymysql')
        elif name == 'sqlite3':
            assert __import__('sqlite3')
            self.__shouldnt_import('MySQLdb')
            self.__shouldnt_import('pymysql')
            self.__shouldnt_import('psycopg2')

    def test_set_dbapi(self):
        database.set_dbapi(dbapi)
        assert database.dbapi.module.__name__ == dbapi_name


class TestDatabase(Test):

    def setUp(self):
        self.database = DatabaseType()
        self.database.set_dbapi(dbapi)
        super(TestDatabase, self).setUp()

    def test_config(self):
        assert self.database.configs == {}
        self.database.config(**configs)
        assert self.database.configs
        assert not self.database.conn
        self.database.connect()
        assert self.database.conn
        self.database.config(**configs)
        assert not self.database.dbapi.conn_is_open(self.database.conn)

    def test_connect(self):
        assert self.database.conn is None
        self.database.config(**configs)
        conn1 = self.database.connect()
        conn2 = self.database.connect()
        assert conn1 is not conn2
        assert self.database.dbapi.conn_is_open(conn1)
        assert self.database.dbapi.conn_is_open(conn2)
        assert self.database.dbapi.get_autocommit(self.database.conn) is True

    def test_get_conn(self):
        assert self.database.conn is None
        self.database.config(**configs)
        conn = self.database.get_conn()
        assert conn and self.database.dbapi.conn_is_open(conn)
        assert conn and self.database.dbapi.conn_is_alive(conn)
        conn1 = self.database.get_conn()
        assert conn1 is conn

    def test___del__(self):
        self.database.config(**configs)
        self.database.connect()
        conn = self.database.conn
        dbapi = self.database.dbapi
        del self.database
        assert not dbapi.conn_is_open(conn)

    def test_execute(self):
        self.database.config(**configs)
        cursor = self.database.execute(
            "insert into t_user (name, email) values ('jack', 'i@gmail.com')")
        if db_type == 'postgres':
            assert cursor.lastrowid == 0
        else:
            assert cursor.lastrowid == 1

    def test_execute_sql(self):
        pass

    def change(self):
        self.database.configs(**configs)
        self.database.connect()
        old_conn = self.database.conn
        self.database.execute('create database skylarktests2')
        self.database.change('skylarktests2')
        assert self.database.configs != configs
        if db_type == 'mysql':
            self.database.conn is old_conn
        else:
            self.database.conn is not old_conn
            assert not self.database.dbapi.conn_is_open(old_conn)
