.. _tips:

小贴士
======

.. Contents::

善用destroy()
-------------

如果仅仅是为了删除一条记录的话，只要::

    User.at(2).delete()

而如下的做法是不推荐的, 因为一查一删执行了两次SQL查询::

    user = User.at(2).getone()
    user.destroy()  # 共执行了两次查询

同样道理还有 ``update``::

    >>> user = User.at(7).getone()
    >>> user.name = 'ANewNAme'
    >>> user.save()  # 如果只是为了更新这一行 
    1L
    >>> User.at(7).update(name='ANewNAme').execute()  # 这样做更好
    1L

怎样获取结果集行数
------------------

不要使用Python来获取结果集的行数::

    >>> users = User.getall()
    >>> len(tuple(users)) # BAD
    4

而要使用 ``result.count`` ::

    >>> result = User.select().execute()
    >>> result.count  # GOOD
    4L

``count`` 属性存储了结果集的行数，这个信息是来自于mysql的，所以我们设计为一个属性
``result.count`` 而不是 ``result.count()`` , 它是一个已经存在的数据而不是我们计算得到的。

使用SQL合计函数
---------------

如果你仅仅想知道表里有多少个用户, 使用合计函数 ``count``, 而不要
取出所有的用户然后返回结果集的行数(虽然这样也可以，但对于mysql而言
执行两个语句的速度上这样慢)::

    >>> User.count()  # GOOD
    4L

    >>> query = User.select()  # 仅仅查询行数的话,
    >>> result = query.execute()  # 不推荐这样做, BAD
    >>> result.count
    4L

测试一条记录的存在性
--------------------

比如，在数据库中是否有一个人叫做Jack呢::

    >>> jack = User(name='Jack')
    >>> jack in User
    True

使用datetime对象
----------------

CURD.py支持数、字符串和dateime对象等多种类型的Python对象来映射到SQL语句中，推荐使用datetime对象
而不是使用相应的字符串。

推荐的做法::

    >>> from datetime import datetime
    >>> Post.at(1).update(update_at=datetime(2014, 1, 15))
    <UpdateQuery "update post set post.update_at = '2014-01-15 00:00:00' where post.post_id = '1'">

虽然这样也构造了完全相同的update查询语句，但是不推荐这样做::

    >>> Post.at(1).update(update_at='2014-01-15 00:00:00')
    <UpdateQuery "update post set post.update_at = '2014-01-15 00:00:00' where post.post_id = '1'">

查询得到的时间类型的字段也会是datetime对象::

    >>> post = Post.at(1).getone()
    >>> post.update_at
    datetime.datetime(2013, 11, 11, 11, 11, 11)

在Python中我们一如既往地推荐使用datetime对象而不是字符串来处理时间和日期。

.. _tip_database_change:

数据库切换
----------

切换数据库的话，Database.change(db_name)好于Database.config(db=db_name)，也就说，
使用我们给出的特定方法 ``change`` 而不是使用更新数据库连接配置的方式来切换数据库。

使用 ``Database.change(db_name)`` 而不是 ``Database.config(db=db_name)`` 来切换数据库。
后者会关闭当前活动的数据库连接（如果存在的话）并在必要的时候重新开一个数据连接，而前者
不必关闭数据库连接直接切换数据库。

混合自定义方法到模型类
----------------------

如果基本模型类Model没有我们期待的接口方法，我们可以自己混合自定义方法绑定给它，这不是
CURD.py带来的技术，Python中称之为mix-in技术。

比如为了获取id为3的用户::

    >>> User.at(3).getone()
    <models.User object at 0xb7040d6c>

更短的写法可以是::

    >>> from CURD import MetaModel
    >>> MetaModel.__getitem__ = lambda model, index: model.at(index).getone()
    >>> User[3]
    <models.User object at 0xb62eb78c>

把所有模型类统一定义入一个Python脚本中
--------------------------------------

当我们用CURD.py写一个app的时候，推荐把所有的模型类写到一个py脚本中去。

比如我们把所有模型类写到 ``models.py`` 中去:

.. literalinclude:: ../sample/models.py

在其他地方使用模型的时候::

    from models import User
    query = User.select()  # etc..


-------------


欢迎更多的贴士， 请提到issue: https://github.com/hit9/CURD.py/issues
