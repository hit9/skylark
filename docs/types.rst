Type Mappings
=============

.. Contents::

Python values will be mapped to SQL string literals in order to
make a legal SQL command::

    >>> query = Post.insert(
    ...   title='helloworld',  # str
    ...   content=u'你好',     # unicode
    ...   create_at=datetime.now(), # datetime object
    ...   is_published=False  # bool
    ... )
    >>> print query.sql
    insert into post set post.content = '你好', post.is_published = 0, post.create_at = '2013-11-22 10:59:57', post.title = 'helloworld'


Type mapping is required if we want to talk to mysql in Python language,
CURD.py maps these types(shown in examples):

============  =====================  ======================
Python Type   Python Value Example   SQL Literal
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
