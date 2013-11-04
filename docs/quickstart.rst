.. _quickstart:

Quick Start
===========

.. Contents::

.. _DatabaseConfig:

Database Configuration
----------------------

``db``, ``user``, ``passwd`` are required::

    Database.config(db='mydb', user='root', passwd='')

.. _DefineModel:

Define Model
------------

::

    class User(Model):
        name = Field()
        email = Field()
        # default primarykey: `id`, to figure out primarykey :
        #   myid = PrimaryKey()


All models are inherited from Model.
We take **the lower case of model's classname as table's name**

Better to put all models in a single script,  name it ``models.py`` :

.. _two_models:

.. literalinclude:: sample/models.py

*Note: sql defination of these two tables is* `here
<https://github.com/hit9/CURD.py/blob/master/tests/tables.sql>`_.

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
    3L  # inserted primarykey's value

or this way :)
::

    >>> user=User(name='jack',email='jack@gmail.com')
    >>> user.save()
    4L

.. _Update:

Update
------

Simply, just ``save``

::

    >>> user.name = 'Any'
    >>> user.save()  # return 0 for failure,else success
    1L  # rows affected

or ::

    >>> User.at(3).update(name='Any')
    1L

tip: ``User.at(id_value)`` is equivalent to ``User.where(User.id == id_value)``, both return class ``User``

.. _Read:

Read
----

::

    >>> select_result = User.where(name='Any').select()
    >>> for user in select_result.fetchall():
    ...     print user.name,user.email
    ...
    Any jack@gmail.com
    Any jack@gmail.com

The ``name="Any"`` can be replaced by ``User.name == "Any"``

If we select data by primarykey, we can use ``Model.at(int_var)``::

    >>> user=User.at(1).select().fetchone()
    >>> user.name
    u'Jack'


We want all users:

::

    User.select()

We only care about their names:

::

    User.where(User.id > 5).select(User.name)


Method ``select`` returns a ``SelectResult`` object::
    
    >>> User.select()
    <CURD.SelectResult object at 0xb6c1bb2c>

which has 2 methods to fetch results:

- ``fetchone()``: fetch one result each time

- ``fetchall()``: fetch all results at a time

and has an attribute ``count``: result rows count::

    >>> User.select().count
    4L  # rows selected

.. _Delete:

Delete
------

::

    >>> user.destroy()
    1L  # rows affected

or :

::

    >>> User.where(name='Any').delete()
    2L

Both the two methods return affected rows number.

.. _JoinModel:

JoinModel
---------

We defined :ref:`two models <two_models>` in models.py: ``User``, ``Post``

.. literalinclude:: ../sample/models.py

Now, join them::

    >>> Post & User
    <CURD.JoinModel object at 0xb76f292c>


Why not ``User & Post`` ?  The ``&`` operator has direction: it points from main model to foreign model.

Who has wrote posts ?

::

    >>> for post, user in (Post & User).select().fetchall():
    ...     print "%s wrote this post: '%s'" % (user.name, post.name)
    ...
    Jack wrote this post: 'Hello World!'
    Any wrote this post: 'Like Github?'
    James wrote this post: 'You should try travis!'
    Rose wrote this post: 'Be a cool programmer!'

Of course,there are also ``where``, ``orderby``, ``delete``, ``update`` for joinmodels.

For example, to delete Jack's posts::

    >>> (Post & User).where(User.name=='Jack').delete(Post)
    1L
