.. _exceptions:


Exceptions
==========

.. Contents::

CURDException
-------------

There was an ambiguous exception occurred within CURD.py


UnSupportedType
---------------

This Python type is unsupported now.

example::

    >>> User.where(id=object()).select()
    Traceback (most recent call last):
    .....
    CURD.UnSupportedType: Unsupported type '<type 'object'>' in one side of some expression


ForeignKeyNotFound
------------------

Foreign key not found in main model.

example::

    >>> Post.user_id
    <ForeignKey 'post.user_id'>
    >>> Post.user_id.point_to
    <PrimaryKey 'user.id'>
    >>> User & Post
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "../CURD.py", line 828, in __and__
        return JoinModel(self, join)
      File "../CURD.py", line 1078, in __init__
        "'%s' not found in '%s'" % (join.__name__, main.__name__))
    CURD.ForeignKeyNotFound: Foreign key references to 'Post' not found in 'User'

PrimaryKeyValueNotFound
-----------------------

Primarykey value not found in this instance.

example, ``id`` not selected, and CURD.py dont know which row to update::

    >>> user = User.select(User.name).execute().fetchone()
    >>> user.name
    u'Join'
    >>> user.name = 'Julia'
    >>> user.save()
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "../CURD.py", line 968, in save
        raise PrimaryKeyValueNotFound  # need its primarykey value to track this instance
    CURD.PrimaryKeyValueNotFound
