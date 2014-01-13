.. _database:


Database
========

.. Contents::

CURD.py is a tiny orm only for MySQL, it wraps the MySQL-Python package and
behaves like the famous Python orm peewee.

.. _db_configuration:

Database Configuration
----------------------

All available configuration items are here, connections will be auto established with these configs:

======== ========  ====================== ===========
keyword  type      what for               default
======== ========  ====================== ===========
host     string    host to connect        'localhost'
user     string    user to connect as     ''
passwd   string    password for this user ''
db       string    database to use        ''
port     integer   TCP/IP post to connect 3306
charset  string    charset of connection  'utf8'
======== ========  ====================== ===========

See the MySQLdb documentation for more information,
the parameters of `MySQLdb.connect` are all supported.

Generally, you just need to tell CURD.py these 3 items: ``user``, ``passwd``, ``db``::

    >>> Database.config(db='mydb', user='root', passwd='')

Get Database Connection
------------------------

CURD.py will reuse the exist connection in singleton pattern, if you need the connection object::

    >>> Database.get_conn()
    <_mysql.connection open to 'localhost' at 882e174>
    >>> Database.get_conn()  # the same connection object
    <_mysql.connection open to 'localhost' at 882e174>
    >>> Database.get_conn().close()
    >>> Database.get_conn()  # opened a new connection
    <_mysql.connection open to 'localhost' at 8878c4c>

Execute Raw Query
-----------------

If you are dealing tasks outside of CURD.py's abilities, and need to run a raw query::

    >>> Database.execute('show tables')
    <MySQLdb.cursors.Cursor object at 0xb703efcc>


Change Database
---------------

To change database::

    Database.change(db)

or::

    Database.select_db(db)  # alias of `change`


**Note**: Try to use ``Database.change(new_db_name)`` instead of
``Database.config(db=new_db_name)`` , the latter will close the active database
connection and the former needn't.
