.. _faq:

FAQ
===

.. Contents::

Unicode Issue
-------------

Before compiling out a new SQL, CURD.py will encode unicode with ``utf8`` by default::

    >>> User.where(name=u'小明').select(User.id)

the ``u'小明'`` above will be encoded with ``utf8`` at first, and then CURD's 
compiler makes a SQL::

    select user.id from user where user.name = '小明';

If you don't want ``utf8``, set this var::

    CURD.Compiler.encoding = 'gbk'

SQL Injection Problem?
-----------------------

No, strings are escaped before insertion.

Installation trouble: mysql_config not found
---------------------------------------------

I meet problem installing CURD.py: ``mysql_config not found``

Actually, that's MySQL-python's issue, solution:

- for ubuntu users::

     $ apt-get install libmysqlclient-dev

- for mac users::

     $ export PATH=$PATH:/usr/local/mysql/bin

Available Scope
---------------

- CURD.py only works with tables which has a single Field as its primarykey.
