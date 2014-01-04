.. _quickstart:

Quick Start
===========

.. Contents::

.. _DatabaseConfig:

Database Configuration
----------------------

``db``, ``user``, ``passwd`` are required::

    Database.config(db='mydb', user='root', passwd='')

Connection to mysql will be auto established when you execute queries.

See :ref:`db_configuration` for detailed configurations.

.. _DefineModel:

Model Definition
----------------

::

    class User(Model):
        name = Field()
        email = Field()
        # default primarykey: `id`, to figure out primarykey :
        #   myid = PrimaryKey()

We defined a model: ``User``, which has 3 fields:``name``, ``email`` and ``id`` (``'id' is the default primarykey``)

All models should inherit Model.

We take **the lower case of model's classname as table's name**

Better to put all models in a single script,  name it ``models.py`` :

.. _two_models:

.. literalinclude:: sample/models.py

* You have to create tables in MySQL by hand, CURD.py has no feature ``create_tables``

* Note: sql defination of these two tables is `here <https://github.com/hit9/CURD.py/blob/master/tests/tables.sql>`_.

.. _Create:

Create
------

Add "Jack" to datatable:

::

    >>> from models import User
    >>> User.create(name='jack', email='jack@gmail.com')
    <models.User object at 0x8942acc>  # User object

or to use ``save``

::

    >>> user = User()
    >>> user.name = 'jack'
    >>> user.email = 'jack@gmail.com'
    >>> user.save()
    1L  # inserted primarykey's value

or this way :)
::

    >>> user = User(name='jack',email='jack@gmail.com')
    >>> user.save()
    2L

.. _Update:

Update
------

Simply, just ``save``

::

    >>> user.name = 'Any'
    >>> user.save()  # return 0 for failure,else success
    1L  # rows affected

or ::

    >>> query = User.at(2).update(name='Join')
    >>> query
    <UpdateQuery "update user set user.name = 'Join' where user.id = '2'">
    >>> query.execute()
    1L

tip: ``User.at(id_value)`` is equivalent to ``User.where(User.id == id_value)``, both return class ``User``

.. _Read:

Read
----

::

    >>> query = User.where(name='Join').select()
    >>> query
    <SelectQuery "select user.id, user.name, user.email from user where user.name = 'Join'">
    >>> result = query.execute()
    >>> for user in result.fetchall():
    ...   print user.name, user.email
    ...
    Join jack@gmail.com

The ``name="Any"`` can be replaced by ``User.name == "Any"``.

And, we can iter a ``SelectQuery object`` directly, that will execute the
query::


    >>> query = User.where(name='Join').select()
    >>> for user in User.select():
    ...   print user.name, user.email
    ...
    jack jack@gmail.com
    Join jack@gmail.com

If we select data by primarykey, we can use ``Model.at(int_var)``::

    >>> query = User.at(1).select()
    >>> query
    <SelectQuery "select user.id, user.name, user.email from user where user.id = '1'">
    >>> result = query.execute()
    >>> user = result.fetchone()
    >>> user.name, user.id
    (u'jack', 1L)

Model.select
''''''''''''

We want all users:

::

    User.select()

We only care about their names:

::

    User.where(User.id > 5).select(User.name)

SelectResult Object
''''''''''''''''''''

Execute a select query will get a ``SelectResult object``,

which has 2 methods to fetch results:

- ``fetchone()``: fetch one result each time

- ``fetchall()``: fetch all results at a time

and has an attribute ``count``: result rows count::


    >>> query = User.select()
    >>> result = query.execute()
    >>> result.count
    2L  # rows selected

Select Shortcuts
''''''''''''''''

There are 4 methods to select rows quickly: ``findone()``, ``findall()``,
``getone()`` and ``getall()``

sample usage::

    >>> user = User.findone(name='Join')  # <=> User.where(name='Join').select().execute().fetchone()
    >>> user.id
    2L

    >>> users = User.findall(User.id > 0, name='Join') # <=> User.where(User.id > 0 name='Join').select().execute().fetchall()
    >>> [user.name for user in users]
    [u'Join']

    >>> user = User.at(2).getone() # <=> User.where(id=2).select().execute().fetchone()
    >>> user.name
    u'Join'

    >>> users = User.getall() # <=> User.select().execute().fetchall()
    >>> [(user.id, user.name) for user in users]
    [(1L, u'jack'), (2L, u'Join')]

.. _Delete:

Delete
------

::

    >>> user.destroy()
    1L  # rows affected

or :

::

    >>> query = User.at(1).delete()
    >>> query
    <DeleteQuery "delete user from user where user.id = '1'">
    >>> query.execute()
    1L  # rows affected

Both the two methods return affected rows number.

.. _Where:

Where
-----

Method ``where`` seems to be magic::

    Model.where(*expressions, **data)  # returns this `Model` itself

Where Sample Usage
''''''''''''''''''
::

    >>> query = User.where(name='Jack').select()
    >>> query.sql
    "select user.name, user.email, user.id from user where user.name = 'Jack'"

    >>> query = User.where(User.id.between(3,6)).select()
    >>> query.sql
    "select user.id, user.name, user.email from user where user.id between '3' and '6'"

    >>> query = User.where(User.name.like('%sample%')).select()
    >>> query.sql
    "select user.name, user.email, user.id from user where user.name like '%sample%'"

All available expressions are here: :ref:`expressions`

SubQuery
''''''''

An example of subquery using operator ``_in``::

    >>> query = User.where(User.id._in(
    ...   Post.select(Post.user_id)
    ... )).select()
    >>> query.sql
    'select user.id, user.name, user.email from user where user.id in ((select post.user_id from post))'
    >>> [(user.id, user.name) for user in query]  # run this query
    [(3L, u'Join'), (5L, u'Amy')]

Group By
---------

::

    groupby(*Field Objects)

Sample::

    >>> query = User.groupby(User.name).select(User.id, User.name)
    >>> query.sql
    'select user.name, user.id from user group by user.name'

Having
------

::

    having(*Expression Objects)

Sample::

    >>> query = User.groupby(User.name).having(Fn.count(User.id) > 3).select(User.id, User.name)
    >>> query.sql
    "select user.name, user.id from user group by user.name having count(user.id) > '3'"

.. _orderby:

Order By
--------

::

    orderby(Field Object, desc=False)

Sample:

::

    >>> query = User.where(User.id < 5).orderby(User.id, desc=True).select()
    >>> query.sql
    "select user.id, user.name, user.email from user where user.id < '5' order by user.id desc "

Limit
-----

::

    limit(rows, offset=None)

Sample:

::

    >>> query = User.limit(2, offset=1).select()
    >>> query.sql
    'select user.id, user.name, user.email from user limit 1, 2 '

Distinct
--------

::

    distinct()

Sample::

    >>> for user in User.distinct().select(User.name):
    ...   user.name
    ... 
    u'jack'
    u'tom'

Is X In the Table?
---------------------

::

    >>> jack = User(name='Jack')
    >>> jack in User
    True  # there's someone called `Jack` in all users

.. _JoinModel:

JoinModel
---------

We defined :ref:`two models <two_models>` in models.py: ``User``, ``Post``

.. literalinclude:: ../sample/models.py

Now, join them::

    >>> Post & User
    <CURD.JoinModel object at 0xb76f292c>


Why not ``User & Post``:

The ``&`` operator has direction, it points from main model to foreign model.

Who has wrote posts ?

::

    >>> for post, user in (Post & User).select():
    ...   print '%s wrote this post: "%s"' % (user.name, post.name)
    ...
    Jack wrote this post: "Hello wolrd!"
    Amy wrote this post: "I love Python"
    Join wrote this post: "I love GitHub"
    Join wrote this post: "Never Give Up"

Of course,there are also ``where``, ``orderby``, ``delete``, ``update`` for joinmodels.

For example, to delete Jack's posts::

    >>> query = (Post & User).where(User.name == 'Jack').delete(Post)
    >>> query
    <DeleteQuery "delete post from post, user where user.name = 'Jack' and post.user_id = user.id">
    >>> query.execute()
    1L

SQL Functions
-------------

This feature was added in v0.3.1.

An example::

    >>> from CURD import Fn
    >>> query = User.select(Fn.count(User.id))
    >>> query
    <SelectQuery 'select count(user.id) from user'>
    >>> result = query.execute()
    >>> user = result.fetchone()
    >>> user.count_of_id
    4L

In the code above, we use ``Fn.count`` to make a ``Function`` object::

    >>> Fn.count(User.id)
    <Function 'count(user.id)'>

and then use ``user.count_of_id`` to get rows count.

So far, CURD.py supports 5 aggregate functions:

- ``count``
- ``sum``
- ``max``
- ``min``
- ``avg``

and 2 scalar functions

- ``ucase``
- ``lcase``

All these functions are used in the way above, here is function ``ucase``'s
example::

    >>> [user.ucase_of_name for user in  User.select(Fn.ucase(User.name))]
    [u'JOIN', u'JACK', u'AMY', u'JACK']


Shortcuts
''''''''''

In most cases, we don't mix functions and fields in the same query, for
instance, we just need the count of a table's rows.

We can just do it this way::

    >>> User.count()
    4L

Similarly, all aggregate functions have this feature::

    >>> User.count()
    4L
    >>> User.max(User.id)
    6L
    >>> User.min(User.id)
    3L
    >>> User.sum(User.id)
    Decimal('18')
    >>> User.avg(User.id)
    Decimal('4.5000')
