.. _quickstart:

Quick Start
===========

.. rst-class:: quickstart-toc

    * :ref:`SimpleExample`
    * :ref:`DatabaseConfig`
    * :ref:`DefineModel`
    * :ref:`Create`
    * :ref:`Update`
    * :ref:`Read`
    * :ref:`Delete`
    * :ref:`JoinModel`

.. _SimpleExample:

Simple Example
--------------

Codes works with virgo looks like

.. literalinclude:: code/QuickStart/example.py

1. In this code, first we imported the virgo module and configure the Database class.

2. Next we define a model: ``User``, which has 3 fields:``name``, ``email`` and ``id`` (*Note:id is the default primary key*)

3. Then, we create an instance of ``User``.

4. Finally we insert one record into database by calling function ``save``

.. _DatabaseConfig:

Database Configuration
----------------------

``db``, ``user``, ``passwd`` are required:

::

    Database.config(db="mydb", user="root", passwd="")


For more, see :ref:`Database.config`

.. _DefineModel:

Define Model
------------

example:

::

    class User(Model):
        name = Field()
        email = Field()
        # default primarykey is id, to figure out primarykey : 
        # myid = PrimaryKey()


All models are inherited from Model.
virgo regards the lower case of model's classname as its table's name

Put all models in single script `models.py`:

.. literalinclude:: code/QuickStart/models.py

For more.see :ref:`Model`

.. _Create:

Create
------

Record "Jack" to datatable:

::

    >>> from models import User
    >>> User.create(name="jack",email="jack@gmail.com")
    <models.User object at 0x8942acc>

or to use ``save``

::

    >>> user = User()
    >>> user.name = "jack"
    >>> user.email = "jack@gmail.com"
    >>> user.save()  # return primary key's value
    3L

or this way :)
:: 

    >>> user=User(name="jack",email="jack@gmail.com")
    >>> user.save()
    4L

For more about create,see :ref:`Model.create`

.. _Update:

Update
------

Simply,just `save`

::

    >>> user.name = "Any"
    >>> user.save()  # return 0 for failure,else success
    1

or ::

    >>> User.at(3).update(name="Any")
    1

``User.at(id_value)`` is equivalent to ``User.where(User.id == id_value)``,both return class ``User``

.. _Read:

Read
----

::

    >>> select_result = User.where(name="Any").select()
    >>> for user in select_result.fetchall():
    ...     print user.name,user.email
    ... 
    Any jack@gmail.com
    Any jack@gmail.com

The ``name="Any"`` can be replaced by ``User.name == "Any"``

If we select data by primarykey, we can use ``Model.at(int_var)`` :

::

    >>> user=User.at(1).select().fetchone()
    >>> user.name
    u'Jack'


We want all users:

::

    User.select()

We only care about their names:

::
    
    User.where(User.id > 5).select(User.name)

Is there someone in the table called 'James'?

::

    >>> user=User(name="James")
    >>> user in User
    False

We record 'new users' only:

::

    user = User(name="Mark")

    if user not in User:
        user.save()
    else:
        exit("Already in database!")

.. _Delete:

Delete
------

::

    >>> user.destroy()
    1

or :

::

    >>> User.where(name="Any").delete()
    2

Both the two methods return affected rows number. 

For more,see :ref:`Model.Delete`

.. _JoinModel:

JoinModel
---------

We defined two models in models.py , ``User,Post``

.. literalinclude:: code/QuickStart/models.py

Now,join them:

::
    
    >>> Post & User
    <virgo.JoinModel object at 0x8a6c26c>

Why not ``User & Post`` ? try it yourself.


Who has wrote posts ?

::

    >>> for post,user in (Post & User).select().fetchall():
    ...     print "%s write this post: '%s'" % (user.name, post.name)
    ... 
    Jack write this post: 'Hello World!'
    Any write this post: 'Like Github?'
    James write this post: 'You should try travis!'
    Rose write this post: 'Star virgo!'

Of course,there are ``where,orderby,delete,update`` for joinmodel.

Delete Jack's posts:

:: 

    >>> (Post & User).where(User.name=="Jack").delete(Post)
    1


