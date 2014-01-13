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

The same tip with ``update``::

    >>> user = User.at(7).getone()
    >>> user.name = 'ANewNAme'
    >>> user.save()  # if you just want to update this row
    1L
    >>> User.at(7).update(name='ANewNAme').execute()  # this way is better
    1L

How to count result rows
------------------------

Don't count select results this way::

    >>> users = User.getall()
    >>> len(tuple(users))  # Don't use Python to count
    4

Use ``result.count`` instead::

    >>> result = User.select().execute()
    >>> result.count  # but use the information comes from mysql
    4L

The ``count`` stores the result's rows number, it comes from mysql,
that's why we use ``result.count`` but not ``result.count()``, it's
data already there but not data to query.

Use SQL functions shortcuts
---------------------------

If you just want to know how many rows are in table ``user``,
just count, don't do a select query::

    >>> User.count()  # clean and fast
    4L
    >>> query = User.select()  # if you just want to count table `user`
    >>> result = query.execute()  # this way is BAD
    >>> result.count
    4L

Test if an except record is in the table
---------------------------------------------

Is there someone called 'Jack' in database? ::

    >>> jack = User(name='Jack')
    >>> jack in User
    True

Use datetime object in queries
-------------------------------

CURD.py now support numbers, strings and datetime objects as values to
insert(or update) into table.

::

    >>> Post.at(1).update(update_at=datetime.now())
    <UpdateQuery "update post set post.update_at = '2013-11-21 16:55:16' where post.id = '1'">


This field can be select as datetime objects as well::

    >>> post = Post.at(1).getone()
    >>> post.update_at
    datetime.datetime(2013, 11, 11, 11, 11, 11)

Using Python's ``datetime`` to handle time values is much better than using
strings.

.. _tip_database_change:

Database.change(db_name) better to Database.config(db=db_name)
--------------------------------------------------------------

To select a new database, use ``Database.change(db_name)`` instead of ``Database.config(db=db_name)``,
the latter will close the active database connection and the former needn’t.

mix your methods into Model
---------------------------

To get the user whose id is 3 (suppose id is the primary key)::

    >>> User.at(3).getone()
    <models.User object at 0xb7040d6c>

A shorter one::

    >>> from CURD import MetaModel
    >>> MetaModel.__getitem__ = lambda model, index: model.at(index).getone()
    >>> User[3]
    <models.User object at 0xb62eb78c>

Of course, the "Mix-in" is not CURD.py's own skill, python developers play with
it everywhere.

Put all models in one script in your app
----------------------------------------

When we are building web apps with CURD.py, it's good to pull all models into
one script.

in models' file: models.py:

.. literalinclude:: ../sample/models.py

and in other scripts : ::

    from models import User
    query = User.select()  # etc..
