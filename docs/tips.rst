.. _tips:

Some Tips
=========

.. Contents::

.. _tip_destroy:

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
    1
    >>> User.at(7).update(name='ANewNAme').execute()  # this way is better
    1

How to count result rows
-------------------------

Don't count select results this way::

    >>> users = User.getall()
    >>> len(tuple(users))
    4

But use ``result.count`` instead::

    >>> result = User.select().execute()
    >>> result.count
    4

Use SQL functions shortcuts
---------------------------

If you just want to know how many rows are in table ``user``,
just count, don't do a select query::

    >>> User.count()  # clean and fast
    4
    >>> query = User.select()  # if you just want to count table `user`
    >>> result = query.execute()  # this way is BAD
    >>> result.count
    4

Test if an except record is in the table
----------------------------------------

Is there someone called 'Jack' in database? ::

    >>> jack = User(name='Jack')
    >>> jack in User
    True

Use python object directly in queries
--------------------------------------

Type mapping is handled by db connectors, we can use python objects in queries directly,
and needn't to cast data to string format in advance.

For example, insert one record(column ``update_at``'s type is ``datetime``)::

    >>> from datetime import datetime
    >>> Post.create(name='hello world', user_id=1, update_at=datetime.now())
    <models.Post object at 0x1081e21d0>

With sqlite3, this column is selected as a string::

    >>> Post.at(1).getone().update_at
    u'2014-05-23 22:56:10.686144'

But with MySQLdb/PyMySQL, this column is selected as a datetime object::

    >>> Post.at(1).getone().update_at
    datetime.datetime(2014, 5, 23, 23, 5, 57)

Change Database
----------------

To select a new database, use ``Database.change(db_name)`` instead of ``Database.config(db=db_name)``,
because when with mysql, the latter will close the active database connection and the former needn’t.

Put all models in one script in your app
----------------------------------------

When we are building web apps with skylark, it's good to pull all models into
one script.

in models' file: models.py:

.. literalinclude:: ../sample/models.py

and in other scripts : ::

    from models import User
    query = User.select()  # etc..
