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

Python Objects to SQL Literals
------------------------------

Type mapping is required if we want to talk to mysql in Python language,
skylark maps these types(shown in examples):

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
time          time(11,18,04)         '11:18:04'
timedelta     timedelta(minutes=12)  '0 0:12:0'
============  =====================  ======================

MySQL Data to Python Objects
----------------------------

The rules how MySQL types are mapped to Python types:

================================  ==================
MySQL Data Type                   Python Type
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

here are some examples:

====================   ==================================
MySQL Data Example     Python Object
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
