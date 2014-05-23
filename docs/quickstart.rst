.. _quickstart:

QuickStart
==========

.. Contents::


Create Tables
-------------

Skylark dosen't have methods to create or drop tables, we need to
do it manually.

With sqlite3 as an example:

.. code-block:: sql

    $ sqlite3 mydb
    sqlite> create table user(id integer primary key autoincrement, name varchar(33), email varchar(33));
    sqlite> create table post(post_id integer primary key autoincrement, name varchar(100), user_id integer, foreign key(user_id) references t_user(id));

Set DB Connector
----------------

Skylark will try to load connectors in this order: MySQLdb, pymysql, sqlite3,
and use the connector found.

To explicitly tell skylark to use a connector::

    import sqlite3
    from skylark import Database

    Database.set_dbapi(sqlite3)

Database Configuration
----------------------

For sqlite3::

    Database.config(db='mydb')

For mysql::

    Database.config(db='mydb', user='root', passwd='')

Connection to database will be auto established when you execute queries.

.. _DefineModel:

Model Definition
----------------

::

    from skylark import Model, Field

    class User(Model):
        name = Field()
        email = Field()

We defined a model: ``User``, which has 3 fields: ``name``, ``email``, and
``id`` (``id`` is the default primary key).

Better to put all models into a single script, name it ``models.py``:

.. _two_models:

.. literalinclude:: ../sample/models.py

Create
------

Add "jack" to database::

    >>> from models import User
    >>> User.create(name='jack', email='jack@gmail.com')
    <models.User object at 0x100c4a6d0>

or use ``save``::

    >>> user = User()
    >>> user.name = 'jack'
    >>> user.email = 'jack@gmail.com'
    >>> user.save()
    2  # last insert id

which equal to::

    >>> user = User(name='jack',email='jack@gmail.com')
    >>> user.save()
    3

Update
------

Just ``save``::

    >>> user.name = 'Any'
    >>> user.save()
    1  # rows affected

or make a query::

    >>> query = User.at(2).update(name='join')
    >>> query.execute()
    1  # rows affected

*Note: User.at(value) is User.where(id=value).*

Read
----

An example::

    >>> query = User.where(name='jack').select()
    >>> result = query.execute()
    >>> users = result.all()
    >>> [(user.id, user.name) for user in users]
    [(1, u'jack')]

Iterating a select-query will execute the query directly::

    >>> [user.name for user in User.where(User.id >= 3).select()]
    [u'Any']

To select record by primarykey, use ``at()``::

    >>> query = User.at(1).select()
    >>> result = query.execute()
    >>> user = result.one()
    >>> user.id, user.name
    (1, u'jack')

which equal to::

    >>> user = User.at(1).getone()
    >>> user.id, user.name
    (1, u'jack')

select
''''''

We want all users::

    User.select()

We only care about their names::

    User.select(User.name)

select-result
'''''''''''''

Execute a select-query will get a “select-result”, which binds 3 methods for retrieving data::

    >>> result.one()
    <models.User object at 0x100c4a990>

    >>> [user for user in result.all()]
    [<models.User object at 0x100c4a850>]

    >>> result.tuples()
    ((1, u'jack', u'jack@gmail.com'),)

and an attribute ``count``::

    >>> query = User.select()
    >>> result = query.execute()
    >>> result.count
    3L  # rows selected


Quick Read
''''''''''

4 methods to select rows quickly: ``findone()``, ``findall()``,
``getone()``, ``getall()``::

    >>> user = User.findone(name='join')
    >>> user.id
    2

    >>> users = User.findall(User.id > 0, name='jack')
    >>> [user.name for user in users]
    [u'jack']

    >>> user = User.at(2).getone()
    >>> user.name
    u'join'

    >>> users = User.getall()
    >>> [(user.id, user.name) for user in users]
    [(1, u'jack'), (2, u'join'), (3, u'Any')]

Delete
------
::

    >>> user.destroy()
    1L  # rows affected

or::

    >>> query = User.at(1).delete()
    >>> query.execute()
    1L  # rows affected

Where
------

Sample::

    >>> query = User.where(name='jack').select(User.id)
    >>> query.sql
    <sql 'select user.id from user where user.name = ?' ('jack',)>

    >>> query = User.where(User.id.between(3, 6)).select(User.name)
    >>> query.sql
    <sql 'select user.name from user where user.id between ? and ?' (3, 6)>

    >>> query = User.where(User.name.like('%sample%')).select(User.name)
    >>> query.sql
    <sql 'select user.name from user where user.name like ?' ('%sample%',)>

SubQuery
'''''''''

An example of subquery using operator ``_in``::

    >>> from models import Post
    >>> query = User.where(User.id._in(Post.select(Post.user_id))).select(User.id)
    >>> query.sql
    <sql 'select user.id from user where user.id in (select post.user_id from post)' ()>
    >>> [user.id for user in query]
    [1]

this query can also be written using ``join``::

    >>> query = User.join(Post).select(User.id)
    >>> query.sql
    <sql 'select user.id from user join post on post.user_id = user.id' ()>
    >>> [user.id for user in query]
    [1]

Group By
--------

::

    >>> query = User.groupby(User.name).select(User.name, fn.count(User.id))
    >>> query.sql
    <sql 'select user.name, count(user.id) from user group by user.name' ()>
    >>> result = query.execute()
    >>> [(name, count) for name, count in result.tuples()]
    [(u'Any', 1), (u'jack', 2), (u'join', 1)]


Having
------

::

    >>> from skylark import sql
    >>> query = User.groupby(User.name).having(sql('count') > 1).select(User.name, fn.count(User.id).alias('count'))
    >>> query.sql
    <sql 'select user.name, count(user.id) as count from user group by user.name having count > ?' (1,)>
    >>> result = query.execute()
    >>> [(name, count) for name, count in result.tuples()]
    [(u'jack', 2)]

Order By
--------

::

    orderby(field, desc=False)

Sample::

    >>> query = User.where(User.id < 5).orderby(User.id, desc=True).select(User.id)
    >>> [user.id for user in query]
    [4, 3, 2, 1]

Limit
------

::

    limit(rows, offset=None)

Sample::

    >>> query = User.limit(2, offset=1).select()
    >>> query.sql
    <sql 'select user.id, user.name, user.email from user limit 1, 2' ()>

Distinct
--------

::

    >>> from skylark import distinct
    >>> [user.name for user in User.select(distinct(User.name))]
    [u'jack', u'join', u'Any']

And an example for function(distinct)::

    >>> query = User.select(fn.count(distinct(User.name)))
    >>> result = query.execute()
    >>> result.tuples()[0][0]
    3

Is X In the Table?
------------------

::

    >>> jack = User(name='Jack')
    >>> jack in User
    True  # there's someone called `Jack` in all users

Alias
-----

``alias()`` is only avaliable for fields and functions.

::

    >>> query = User.select(User.name.alias('username'))
    >>> query.sql
    <sql 'select user.name as username from user' ()>
    >>> [user.username for user in query]
    [u'Jack', u'Join', u'Amy', u'jack', u'amy']

    >>> query = User.select(fn.count(User.id).alias('count_id'))
    >>> query.sql
    <sql 'select count(user.id) as count_id from user' ()>


SQL
----

::

    sql(literal, *params)

``sql()`` creates a SQL string literal, for example::

    >>> query = User.having(sql('count') > 2).groupby(User.name).select(fn.count(User.id).alias('count'), User.name)
    >>> query.sql
    <sql 'select count(user.id) as count, user.name from user group by user.name having count > ?' (2,)>


Join
-----

Skylark support ``left join``, ``(inner) join``, ``right join`` and ``full join``::

    join(model, on=None, prefix=None)

samples::

    >>> query = User.join(Post).select(User.id)
    >>> query.sql
    <sql 'select user.id from user join post on post.user_id = user.id' ()>

    >>> query = User.left_join(Post).select(User.id)
    >>> query.sql
    <sql 'select user.id from user left join post on post.user_id = user.id' ()>

    >>> query = User.right_join(Post).select(User.id)
    >>> query.sql
    <sql 'select user.id from user right join post on post.user_id = user.id' ()>

    >>> query = User.full_join(Post).select(User.id)
    >>> query.sql
    <sql 'select user.id from user full join post on post.user_id = user.id' ()>

SQL Functions
-------------

An example to count users::

    >>> from skylark import fn
    >>> query = User.select(fn.count(User.id))
    >>> result = query.execute()
    >>> result.tuples()[0][0]
    4

this equal to::

    >>> User.count()
    4

Another example to get upper case of names::

    >>> query = User.select(fn.upper(User.name))
    >>> result = query.execute()
    >>> result.tuples()
    ((u'JACK',), (u'JOIN',), (u'ANY',), (u'JACK',))

Aggregators
''''''''''''

There are 5 built-in aggregator functions for modles: 
``count()``, ``max()``, ``min()``, ``sum()``, ``avg()``::

    >>> User.count()
    4
    >>> User.max(User.id)
    4
    >>> User.min(User.id)
    1
    >>> User.sum(User.id)
    10
    >>> User.avg(User.id)
    2.5
    >>> User.where(User.id > 1).count()
    3
