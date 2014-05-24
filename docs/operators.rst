.. _operators:

Operators
=========

Common Operators
----------------

Skylark maps these common operators (shown in examples):

=======================       =========================
Expressions                   SQL string
=======================       =========================
User.id < 3                   user.id < 3
User.id > 3                   user.id > 3
User.id <= 3                  user.id <= 3
User.id >= 3                  user.id >= 3
User.id == 3                  user.id = 3
User.id != 3                  user.id <> 3
User.id + 2                   user.id + 2
User.id - 2                   user.id - 2
User.id * 2                   user.id * 2
User.id / 2                   user.id / 2
User.id % 2                   user.id % 2
User.name.like('a%')          user.name like 'a%'
User.id._in(1, 2, 3)          user.id in (1, 2, 3)
User.id.not_in(1, 2)          user.id not in (1, 2)
User.id.between(3, 6)         user.id between 3 and 6
expression & expression       expression and expression
expression | expression       expression or expression
=======================       =========================

And the invert version is also valid for exchangeable operators(like ``+``, ``-``..)::

    >>> query = User.where(3 > User.id).select(User.name)
    >>> query.sql
    <sql 'select user.name from user where user.id < ?' (3,)>

    >>> query = User.select(1 + User.id)
    >>> query.sql
    <sql 'select ? + user.id from user' (1,)>

Custom Operator
---------------

The method ``op()`` can help us build custom operators(such as bitwise
operators).

An example for logical and ``&``::

    >>> query = User.select(User.id.op('&')(1))
    >>> query.sql
    <sql 'select user.id & ? from user' (1,)>

And an example for logical invert ``~``::

    >>> from skylark import sql
    >>> query = User.select(sql('').op('~')(User.id))
    >>> query.sql
    <sql 'select ~ user.id from user' ()>

Applicable objects
-------------------

All common operators and method ``op()`` can be used with these objects:
``sql``, ``field``, ``function``, ``expression``.
