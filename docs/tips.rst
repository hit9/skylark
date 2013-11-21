.. _tips:

Some Tips
=========

.. Contents::

Use destroy() wisely
--------------------

To delete one record.

::

    User.at(2).delete()

is better than ::

    user = User.at(2).getone()
    user.destroy()  # this queried 2 times

The same tip with ``update``.

How to count result rows
------------------------

Dont count select results this way::

    >>> users = User.getall()
    >>> len(tuple(users))
    4

Use ``result.count`` instead::

    >>> result = User.select().execute()
    >>> result.count
    4L

If you just want to know how many rows are in table ``user``,
just count, don't do a select query::

    >>> User.count()
    4L

Test whether an except record is in the table
---------------------------------------------

Is there someone called 'Jack' in database? ::

    jack = User(name='Jack')
    if jack in User:
        print "Yes!"

Use datetime object in queries
-------------------------------

CURD.py now support numbers, strings and datetime objects as values to
insert(or update) into table.

::

    >>> Post.at(1).update(datetime=datetime.now())
    <UpdateQuery "update post set post.datetime = '2013-11-21 16:55:16' where post.id = 1">


This field will be select as datetime objects as well::

    >>> post = Post.at(1).getone()
    >>> post.datetime
    datetime.datetime(2013, 11, 11, 11, 11, 11)

mix your methods into Model
---------------------------

To get the user whose id is 3 (suppose id is the primary key)::

    user = User.at(3).getone()

Too long ?

A shorter one::

    def getitem(model,index):
        return model.at(index).getone()
    MetaModel.__getitem__ = getitem

use ``[]`` to do this::

    user=User[1]

Put all models in one script in your app
----------------------------------------

in models' file: models.py:

.. literalinclude:: sample/models.py

and in other scripts : ::

    from models import User
    query = User.select()  # etc..
