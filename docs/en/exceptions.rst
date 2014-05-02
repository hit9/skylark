.. _exceptions:


Exceptions
==========

.. Contents::

SkylarkException
-------------

There was an ambiguous exception occurred within Skylark.


UnSupportedType
---------------

This Python type is unsupported now.

example::

    >>> User.where(id=object()).select()
    Traceback (most recent call last):
    .....
    skylark.UnSupportedType

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
    .....
    skylark.ForeignKeyNotFound

PrimaryKeyValueNotFound
-----------------------

Primarykey value not found in this instance.

example, ``id`` not selected, and skylark dosen't know which row to update::

    >>> user = User.select(User.name).execute().one()
    >>> user.name
    u'Join'
    >>> user.name = 'Julia'
    >>> user.save()
    Traceback (most recent call last):
    .....
        raise PrimaryKeyValueNotFound  # need its primarykey value to track this instance
    skylark.PrimaryKeyValueNotFound
