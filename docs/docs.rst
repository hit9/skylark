.. Contents::

.. _quickstart:

Quick Start
===========

.. _DatabaseConfig:

Database Configuration
----------------------

``db``, ``user``, ``passwd`` are required::

    Database.config(db="mydb", user="root", passwd="")

.. _DefineModel:

Define Model
------------

::

    class User(Model):
        name = Field()
        email = Field()
        # default primarykey is id, to figure out primarykey :
        # myid = PrimaryKey()


All models are inherited from Model.
We take **the lower case of model's classname as table's name**

Better to put all models in a single script,  such as ``models.py`` :

.. literalinclude:: sample/models.py

.. _Create:

Create
------

Add "Jack" to datatable:

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

.. _Update:

Update
------

Simply, just ``save``

::

    >>> user.name = "Any"
    >>> user.save()  # return 0 for failure,else success
    1

or ::

    >>> User.at(3).update(name="Any")
    1

``User.at(id_value)`` is equivalent to ``User.where(User.id == id_value)``, both return class ``User``

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

.. _JoinModel:

JoinModel
---------

We defined two models in models.py: ``User``, ``Post``

.. literalinclude:: ../sample/models.py

Now,join them::

    >>> Post & User
    <CURD.JoinModel object at 0xb76f292c>


Why not ``User & Post`` ? try it yourself.


Who has wrote posts ?

::

    >>> for post,user in (Post & User).select().fetchall():
    ...     print "%s write this post: '%s'" % (user.name, post.name)
    ...
    Jack write this post: 'Hello World!'
    Any write this post: 'Like Github?'
    James write this post: 'You should try travis!'
    Rose write this post: 'Be a cool programmer!'

Of course,there are ``where,orderby,delete,update`` for joinmodel.

Delete Jack's posts::

    >>> (Post & User).where(User.name=="Jack").delete(Post)
    1


.. _Sugar:

Sytactic Sugar
==============

Just some syntatic sugar for CURD.py, to enable them::

    from CURD import Sugar

But, be careful to use the sugar.

Get Item
--------

example::

    >>> user=User[2] 
    >>> user.name 
    u'Amy'

It's just a quick way to run this line codes::
   
    user=User.where(User.primarykey == 2).select().fetchone()

Slice
-----

example::

    >>> users=User[1:3] 
    >>> for user in users: 
    ...     print user.id,user.name
    ...  
    1 Jack
    2 Amy
    3 James

It's just a quick way of::

    users=User.where(User.primarykey >= start, User.primarykey <= end)

And, ``User[start:]``, ``User[:end]``, ``User[:]`` also work::

    >>> User[:3] 
    <generator object fetchall at 0x8a5f9dc>
    >>> User[1:]
    <generator object fetchall at 0x8a5f9b4>
    >>> User[:]
    <generator object fetchall at 0x8a5fa04>

In
--

Is there someone in the table called "James"?

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


.. _tips:

Some Tips
=========

Use destroy() wisely
--------------------

To delete one record.

::
    
    User.at(2).delete()

is better than ::

    user = User.at(2).select().fetchone()
    user.destroy() # this queried 2 times


Only 7 functions query db
-------------------------

they are: 

::

    select()
    update()
    create()
    delete()
    save()
    destroy()
    model_instance in Model  # actually, it calls function - select()

Test if one record is in the table
----------------------------------

if someone in database called 'Jack'? ::

    user = User(name="Jack")
    if user in User:
        print "Yes!"

**Note: This feature requires Sugar**

mix your methods into Model
---------------------------

To get the user whose id is 3 (suppose id is the primary key)::

    user = User.at(3).select().fetchone()

Too long ?

Let's define a shorter one: ``get(key)`` ::

    @classmethod
    def get(cls, key):
        return cls.at(key).select().fetchone()
    Model.get = get

after this code, you can do the same thing like this::

    user = User.get(3)


Or more shorter::


    def getitem(model,index):
        return model.at(index).select().fetchone()
    MetaModel.__getitem__=getitem

use ``[]`` to do this::

    user=User[1]

Put all models in one script in your app
----------------------------------------

in models' file: models.py:

.. literalinclude:: sample/models.py

and in other scripts : ::

    from models import User
    User.select()  # etc..
