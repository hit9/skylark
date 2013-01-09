.. include:: header.rst

Database
========
::

    class Database

virgo only support MySQL Database.

* classmethod of Database:``Database.execute(SQL)``, ``Database.config(**configs)``

* attributes of class Database:``Database.conn`` , ``Database.query_times`` , ``Database.SQL``

* ``Database.query_times`` : record the times number totally queried

* ``Database.SQL`` :record the SQL string last time executed

config
------

Method:
:: 
    classmethod Database.config(**configs)


Parameters:

::

    -------+-----+------------
    keyword|type |  default value
    -------+-----+-------------
    db     |str  |  ""
    -------+-----+----------
    user   |str  |  ""
    -------+-----+--------
    passwd |str  |  ""
    -------+-----+---------
    debug  |bool |  True
    -------+-----+-------------
    charset|str  | "utf8"
    -------+-----+------------
    port   |int  |  3306
    -------+-----+-------------
    host   |str  | "localhost

