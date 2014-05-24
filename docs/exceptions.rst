.. _exceptions:


Exceptions
==========

.. Contents::


SkylarkException
-------------

There was an ambiguous exception occurred within Skylark.

UnSupportedDBAPI
----------------

This DBAPI is currently not supported.

PrimaryKeyValueNotFound
-----------------------

Primarykey value not found in this instance.

example, when id not selected, and skylark dosen’t know which row to update::

    >>> query = User.at(1).select(User.name)
    >>> result = query.execute()
    >>> user = result.one()
    >>> user.data
    {'name': 'jackx'}
    >>> user.name = 'amy'
    >>> user.save()
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "../skylark.py", line 1103, in save
        raise PrimaryKeyValueNotFound
    skylark.PrimaryKeyValueNotFound

SQLSyntaxError
--------------

SQL syntax error.

ForeignKeyNotFound
--------------------

Raised when the bridge was not found between two models to be joined.
