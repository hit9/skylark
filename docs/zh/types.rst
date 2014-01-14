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

当我们在Python和SQL之间对话的时候，类型映射是不可避免的，CURD.py对类型映射有如下约定:

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
time          time(11,18,04)         time(11,18,04)
timedelta     timedelta(minutes=12)  '0 0:12:0'
============  =====================  ======================
