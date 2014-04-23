.. _quickstart:

Quick Start
===========

.. Contents::

.. _DatabaseConfig:

Database Configuration
----------------------

::

    Database.config(db='mydb', user='root', passwd='')

Connection to mysql will be auto established when you execute queries.

For detailed configurations: :ref:`db_configuration`.

.. _DefineModel:

Model Definition
----------------

::

    class User(Model):
        name = Field()
        email = Field()

We defined a model: ``User``, which has 3 fields:``name``, ``email``
and ``id`` (``id`` - the default primarykey)

To tell CURD.py the ``table_name`` of some model::

    class SomeModel(Model):
        table_name = 'tablename_of_somemodel'

By default, we take the "snake" case of model’s classname as ``table_name``, i.e.::

    class User(Model):  # table_name: 'user'
        pass

    class SomeModel(Model):  # table_name: 'some_model'
        pass

Better to put all models into a single script,  name it ``models.py`` :

.. _two_models:

.. literalinclude:: ../sample/models.py

* You **have to create tables in MySQL by hand**, CURD.py has no feature like ``create_tables``,
  table user and post sql defination: https://github.com/hit9/CURD.py/blob/master/tests/tables.sql.

.. _Create:

Create
------

Add "Jack" to datatable:

::

    >>> from models import User
    >>> User.create(name='jack', email='jack@gmail.com')
    <models.User object at 0x8942acc>  # User instance

or to use ``save``

::

    >>> user = User()
    >>> user.name = 'jack'
    >>> user.email = 'jack@gmail.com'
    >>> user.save()
    1L  # inserted primarykey's value

equal to:

::

    >>> user = User(name='jack',email='jack@gmail.com')
    >>> user.save()
    2L

.. _Update:

Update
------

Just ``save()``

::

    >>> user.name = 'Any'
    >>> user.save()
    1L  # rows affected

or ::

    >>> query = User.at(2).update(name='Join')
    >>> query
    <UpdateQuery "update user set user.name = 'Join' where user.id = '2'">
    >>> query.execute()
    1L

Note: ``User.at(value)`` is ``User.where(id=value)``.

.. _Read:

Read
----

An example:

::

    >>> query =  User.where(name='Join').select()
    >>> result = query.execute()
    >>> users = result.all()
    >>> [(user.id, user.name) for user in users]
    [(2L, u'Join')]



Iterating a select-query will execute the query directly::

    >>> [user.name for user in User.where(User.id > 3).select()]
    [u'jack', u'amy']

To select record by primarykey, use ``at()``::

    >>> query = User.at(1).select()
    >>> result = query.execute()
    >>> user = result.one()
    >>> user.id, user.name
    (1L, u'jack')

which equal to::

    >>> user = User.at(1).getone()
    >>> user.id, user.name
    (1L, u'jack')

select
''''''

We want all fields

::

    User.select()

We only care about their names:

::

    User.select(User.name)

select-result
'''''''''''''

Execute a select-query will get a "select-result", which binds 4 methods for
retrieving data::

    >>> result.one()
    >>> <models.User object at 0x1056acd10>

    >>> [user for user in result.all()]
    [<models.User object at 0x1056b70d0>, <models.User object at 0x1056b7190>]

    >>> tuple(result.tuples())
    ((2L, u'Join', u'jack2@gmail.com'), (3L, u'Amy', u'amy@gmail.com'))

    >>> tuple(result.dicts())
    ({'email': u'jack2@gmail.com', 'id': 2L, 'name': u'Join'}, {'email': u'amy@gmail.com', 'id': 3L, 'name': u'Amy'})


and an attribute ``count``::

    >>> query = User.select()
    >>> result = query.execute()
    >>> result.count
    2L  # rows selected

Quick Read
''''''''''

4 methods to select rows quickly: ``findone()``, ``findall()``,
``getone()``, ``getall()``

::

    >>> user = User.findone(name='Join')  # <=> User.where(name='Join').select().execute().one()
    >>> user.id
    2L

    >>> users = User.findall(User.id > 0, name='Join') # <=> User.where(User.id > 0 name='Join').select().execute().all()
    >>> [user.name for user in users]
    [u'Join']

    >>> user = User.at(2).getone() # <=> User.where(id=2).select().execute().one()
    >>> user.name
    u'Join'

    >>> users = User.getall() # <=> User.select().execute().all()
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
    >>> query.execute()
    1L  # rows affected

.. _Where:

Where
-----

Method ``where`` seems to be magic::

    Model.where(*expressions, **data)  # returns this `Model` itself

Where Sample Usage
''''''''''''''''''
::

    >>> query = User.where(name='Jack').select(User.id)
    >>> query.sql
    "select user.id from user where user.name = 'Jack'"

    >>> query = User.where(User.id.between(3, 6)).select(User.name)
    >>> query.sql
    "select user.name from user where user.id between '3' and '6'"

    >>> query = User.where(User.name.like('%sample%')).select()
    >>> query.sql
    "select user.name, user.email, user.id from user where user.name like '%sample%'"

All available expressions are here: :ref:`expressions`

SubQuery
''''''''

An example of sub-query using operator ``_in``::

    >>> query = User.where(User.id._in(Post.select(Post.user_id))).select()
    # select user.id, user.name, user.email from user where user.id in ((select post.user_id from post))
    >>> [user.id for user in query]
    [1L]

Group By
---------

::

    >>> from CURD import fn
    >>> query = User.groupby(User.name).select(User.name, fn.count(User.id))
    # select user.name, count(user.id) from user group by user.name
    >>> [(user.name, func.count) for user, func in query]
    [(u'Amy', 2L), (u'jack', 2L), (u'Join', 1L)]


Having
------

::

    >>> from CURD import sql
    >>> query = User.groupby(User.name).having(sql('count') > 1).select(User.name, fn.count(User.id).alias('count'))
    # select user.name, count(user.id) as count from user group by user.name having count > '1'
    >>> [(user.name, func.count) for user, func in query]
    [(u'Amy', 2L), (u'jack', 2L)]

.. _orderby:

Order By
--------

::

    orderby(field, desc=False)

Sample::

    >>> query = User.where(User.id < 5).orderby(User.id, desc=True).select(User.id)
    # select user.id from user where user.id < '5' order by user.id desc
    >>> [user.id for user in query]
    [3L, 2L, 1L]


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

    >>> from CURD import distinct
    >>> [user.name for user in User.select(distinct(User.name))]
    [u'jack', u'Join', u'Amy']
    # select distinct(user.name) from user

And an example for ``function(distinct)``:

::

    >>> query = User.select(fn.count(distinct(User.name)))
    # select count(distinct(user.name)) from user
    >>> result = query.execute()
    >>> result.one().count
    3L

Is X In the Table?
------------------

::

    >>> jack = User(name='Jack')
    >>> jack in User
    True  # there's someone called `Jack` in all users

.. _alias:

Alias
-----

``alias()`` is avaliable for fields and functions.

::

    >>> query = User.select(User.name.alias('username'))
    # select user.name as username from user
    >>> [user.username for user in query]
    [u'Jack', u'Join', u'Amy', u'jack', u'amy']

    >>> query = User.select(fn.count(User.id).alias('count_id'))
    # select count(user.id) as count_id from user

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


To update jack's post::

    >>> query = (Post & User).where(User.name == 'Jack').update(Post.name == 'NewName!')
    # update post, user set post.name = 'NewName!' where user.name = 'Jack' and post.user_id = user.id
    >>> query.execute()
    1L

To delete Jack's posts::

    >>> query = (Post & User).where(User.name == 'Jack').delete(Post)
    # delete post from post, user where user.name = 'Jack' and post.user_id = user.id
    >>> query.execute()
    1L


SQL Functions
-------------

Count users::

    >>> from CURD import fn
    >>> query = User.select(fn.count(User.id))
    # select count(user.id) from user
    >>> result = query.execute()
    >>> func = result.one()
    >>> func.count
    5L

equal to::

    >>> User.count()
    5L

Get upper case of names::

    >>> query = User.select(fn.ucase(User.name))
    # select ucase(user.name) from user
    >>> [func.ucase for func in query]
    [u'JACK', u'JOIN', u'AMY', u'JACK', u'AMY']

and distinct these upper cased names::

    >>> query = User.select(distinct(fn.ucase(User.name)))
    # select distinct(ucase(user.name)) from user
    >>> [func.ucase for func in query]
    [u'JACK', u'JOIN', u'AMY']


Concat names and emails!::

    >>> query = User.select(fn.concat(User.name,': ', User.email))
    # select concat(user.name, ': ', user.email) from user
    >>> [func.concat for func in query]
    [u'Jack: jack@gmail.com', u'Join: jack2@gmail.com', ..]

Retrieve Data
''''''''''''''

::

    # select only fields
    >>> [user.name for user in User.at(1).select(User.name)]
    [u'Jack']

    # select only functions
    >>> [func.ucase for func in User.at(1).select(fn.ucase(User.name))]
    [u'JACK']

    # select both
    >>> [(user.name, func.ucase) for user, func in User.at(1).select(fn.ucase(User.name), User.name)] 
    [(u'Jack', u'JACK')]


Aggregators
'''''''''''

Aggregators can be more easy::

    >>> User.count()
    5L
    >>> User.max(User.id)
    7L
    >>> User.min(User.id)
    1L
    >>> User.sum(User.id)
    Decimal('19')
    >>> User.avg(User.id)
    Decimal('3.8000')
