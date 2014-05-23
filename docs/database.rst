.. _database:

Database
========

::

    from skylark import Database

or::

    from skylark import database  # alias of `Database`

Set A DBAPI
------------

Skylark currently supports 3 DBAPI(db connectors):

- for mysql: `MySQLdb(MySQL-python) <https://pypi.python.org/pypi/MySQL-python>`_ 
  or `PyMySQL <https://github.com/PyMySQL/PyMySQL>`_.

- for sqlite: `sqlite3 <https://docs.python.org/2/library/sqlite3.html>`_

Skylark will try to load them in this order: MySQLdb, pymysql, sqlite3, and use
the connector found, to explicitly tell skylark to use a connector::

    import pymysql
    from skylark import Database
    Database.set_dbapi(pymysql)


DB configuration
-----------------

It depends on your connector.

MySQLdb & PyMySQL
''''''''''''''''''

For mysql, all available configuration items are
`here <http://mysql-python.sourceforge.net/MySQLdb.html#functions-and-attributes>`_.

An example::

    Database.config(db='mydb', user='root', passwd='', charset='utf8')

Sqlite3
'''''''

::

    Database.config(db='mydb')

Autocommit
----------

By default, autocommit mode is on, to set this mode::

    Database.set_autocommit(boolean)

Transaction
-----------

*Transaction is supported since v0.9.0.*

An example::

    with Database.transaction():
        User.create(name='jack', email='jack@gmail.com')

We can run a lot of insert queries within a transaction.

Another example::

    t = Database.transaction()

    try:
        User.create(..)   # run queries
    except:
        t.rollback()
    else:
        t.commit()

Change DB
---------

To select another database::

    Database.change(db)

or::
    
    Database.select_db(db)  # alias of `change`

Execute Raw Query
------------------

If you are dealing tasks outside of skylark’s abilities, and need to run a raw query::

    Database.execute(sql, params)
