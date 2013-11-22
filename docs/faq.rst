.. _faq:

FAQ
===

.. Contents::

Unicode Issue
-------------

CURD.py will encode unicode with utf8 encoding by default, before compiling
out a new SQL::

    >>> User.where(name=u'小明').select(User.id)

the ``u'小明'`` above will be encode with ``utf8`` at first, and then CURD's 
compiler makes a SQL::

    select user.id from user where user.name = '小明';

If you don't want utf8, set this var::

    CURD.DATA_ENCODING = 'gbk'  # set to gbk for example

SQL Injection Problem?
-----------------------

No, strings are escaped before insertion.

mysql_config not found
-----------------------

I meet problem installing CURD.py: ``mysql_config not found``

That's MySQL-python's issue, solution:

for ubuntu users::

    $ apt-get install libmysqlclient-dev

for mac users::

    $ export PATH=$PATH:/usr/local/mysql/bin

Available Scope
---------------

CURD.py only works with tables which has primarykey.
