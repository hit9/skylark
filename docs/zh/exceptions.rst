.. _exceptions:


异常类
======

.. Contents::

如下是CURD.py定义的所有异常类。

CURDException
-------------

在CURD.py的处理过程中发生了一个异常。

UnSupportedType
---------------

该Python类型还未被支持。

引发该异常的示例::

    >>> User.where(id=object()).select()
    Traceback (most recent call last):
    .....
    CURD.UnSupportedType: Unsupported type '<type 'object'>' in one side of some expression


ForeignKeyNotFound
------------------

未在主模型类中找到外键。

引发该异常的示例::

    >>> Post.user_id
    <ForeignKey 'post.user_id'>
    >>> Post.user_id.point_to
    <PrimaryKey 'user.id'>
    >>> User & Post
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "../CURD.py", line 828, in __and__
        return JoinModel(self, join)
      File "../CURD.py", line 1078, in __init__
        "'%s' not found in '%s'" % (join.__name__, main.__name__))
    CURD.ForeignKeyNotFound: Foreign key references to 'Post' not found in 'User'

PrimaryKeyValueNotFound
-----------------------

在该实例中没有找到主键(实例的主键字段没有值)。

比如在一次查询中没有提取 ``id``, CURD.py就会不知道如何去更新该实例::

    >>> user = User.select(User.name).execute().fetchone()
    >>> user.name
    u'Join'
    >>> user.name = 'Julia'
    >>> user.save()
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "../CURD.py", line 968, in save
        raise PrimaryKeyValueNotFound  # need its primarykey value to track this instance
    CURD.PrimaryKeyValueNotFound
