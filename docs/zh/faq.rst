.. _faq:

FAQ
===

.. Contents::

Unicode的问题
-------------

一个Unicode对象要映射到SQL语句中去的话，CURD.py会先把这个unicode对象编码为raw字符串，然后
编译为SQL语句::

    >>> User.where(name=u'小明').select(User.id)

默认地，会使用utf8来编码。 上面的 ``u'小明'`` 会用 ``utf8`` 来编码，然后编译出SQL语句::

    select user.id from user where user.name = '小明';

如果需要更改编码方式，比如设置为使用gbk编码::

    CURD.DATA_ENCODING = 'gbk'

SQL注入问题
-----------

不会发生， 字符串在插入数据库前会被转义。

安装问题: mysql_config not found
---------------------------------------------

我在安装CURD.py的时候遇到了问题: ``mysql_config not found``

事实上，这是MySQL-python的问题，不是CURD.py的问题, 解决方案是:

- 对于ubuntu用户::

     $ apt-get install libmysqlclient-dev

- 对于mac用户::

     $ export PATH=$PATH:/usr/local/mysql/bin

可用的范围
----------

- 表必须有主键，目前不支持联合主键
