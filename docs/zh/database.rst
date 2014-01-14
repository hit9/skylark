.. _database:


数据库类
========

.. Contents::

CURD.py 是一个仅仅支持MySQL的小的ORM, 它简单包装了包MySQL-Python, 并看起来很像
著名的Python orm peewee.

.. _db_configuration:

数据库配置
----------

所有的支持的配置项都在这里，CURD.py会自动地根据这些配置建立数据库连接:

======== ========  ====================== ===========
关键字   类型      含义                   默认值
======== ========  ====================== ===========
host     string    数据库所在主机         'localhost'
user     string    登录到mysql的用户名    ''
passwd   string    登录到mysql的密码      ''
db       string    所使用的数据库名字     ''
port     integer   连接所使用的TCP/IP端口 3306
charset  string    连接编码               'utf8'
======== ========  ====================== ===========

可以从MySQLdb的文档获取更多信息， 方法 ``MySQLdb.connect`` 的所有参数都是支持的。

一般地我们仅仅需要告诉CURD.py这三项: 
``user``, ``passwd``, ``db``::

    >>> Database.config(db='mydb', user='root', passwd='')

获取数据库连接
--------------

CURd.py会单例地复用活动的数据库连接，如果你需要获取连接对象::

    >>> Database.get_conn()
    <_mysql.connection open to 'localhost' at 882e174>
    >>> Database.get_conn()  # the same connection object
    <_mysql.connection open to 'localhost' at 882e174>
    >>> Database.get_conn().close()
    >>> Database.get_conn()  # opened a new connection
    <_mysql.connection open to 'localhost' at 8878c4c>

执行原生SQL语句
---------------

如果你在处理一些CURD.py能力范围外的任务，需要执行一条原生SQL的话::

    >>> Database.execute('show tables')
    <MySQLdb.cursors.Cursor object at 0xb703efcc>

这个方法返回的是一个cursor对象，可以看MySQLdb的文档来了解怎么操作它。

切换数据库
----------

函数原型::

    Database.change(db)

或者使用这个函数的别名函数::

    Database.select_db(db)  # `change`的别名

**注意**: :ref:`tip_database_change`
