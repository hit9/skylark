类型映射
========

.. Contents::

为了构造合法的SQL命令，Python值会被"合适地"映射到SQL字符串中去::

    >>> query = Post.insert(
    ...   title='helloworld',  # str
    ...   content=u'你好',     # unicode
    ...   create_at=datetime.now(), # datetime object
    ...   is_published=False  # bool
    ... )
    >>> print query.sql
    insert into post set post.content = '你好', post.is_published = 0, post.create_at = '2013-11-22 10:59:57', post.title = 'helloworld'

当我们在Python和SQL之间对话的时候，类型映射是不可避免的。CURD.py没有在模型类定义的时候要求
告知各个字段的数据类型（很多其他ORM是这样做的），而是依靠如下的约定在Python和SQL之间转换数据类型的。

Python到SQL的类型映射
---------------------

数据类型从Python到SQL的转换规则如下:

============  =====================  ======================
Python类型    例值                   对应的SQL字符串
============  =====================  ======================
NoneType      None                   NULL
IntType       3                      '3'
LongType      4L                     '4'
FloatType     1.45                   1.45
StringType    'helloworld'           'helloworld'
BoolenType    True                   1
UnicodeType   u'中国'                '中国'
datetime      datetime.now()         '2013-11-22 11:16:36'
date          date(2013, 11, 22)     '2013-11-22'
time          time(11,18,04)         '11:18:04'
timedelta     timedelta(minutes=12)  '0 0:12:0'
============  =====================  ======================

当我们使用CURD.py写入数据到mysql的时候，上述类型转换规则决定了Python对象怎样存储到数据库中。


SQL到Python的类型映射
---------------------

MySQL中的数据取到Python中会是怎样的？这完全取决于CURD.py所依赖的包MySQL-python，
以下是MySQL中的类型到Python对象类型的映射规则:

================================  ==================
MySQL数据类型                     对应的Python类型
================================  ==================
NULL                              None
Bit/TinyInt/SmallInt/MediumInt    int
Int/BigInt                        long
Float/Double/Decimal              float
Char/Varchar/Text/TinyText        unicode
Binary/VarBinary                  string
Date                              datetime.date
Time                              datetime.timedelta
Year                              int
Datetime                          datetime.datetime
Timestamp                         datetime.datetime
================================  ==================

以下是一些示例数据：

====================   ==================================
例值                   对应的Python对象
====================   ==================================
NULL                   None
1                      1
123                    123L
1.23                   1.23
'string'               u'string'
'123     '             '123\x00\x00\x00\x00\x00'
1992-04-05             datetime(1992, 04, 05)
17:00:10               timedelta(0, 61210)
1992                   1992
1992-04-05 10:10:00    datetime(1992, 4, 5, 10, 10, 0)
2014-01-15 22:28:06    datetime(2014, 1, 15, 22, 28, 6)
====================   ==================================
