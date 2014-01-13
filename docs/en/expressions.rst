.. _expressions:

Expressions
-----------

A Field object, an operator and another side(string, value etc.) make up an expression.

Here are mappings from expressions to sql strings:

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
User.name.like('a%')          user.name like 'a%'
User.id._in(1, 2, 3)          user.id in (1, 2, 3)
User.id.not_in(1, 2)          user.id not in (1, 2)
User.id.between(3, 6)         user.id between 3 and 6
expression & expression       expression and expression
expression | expression       expression or expression
=======================       =========================

Samples::

    >>> User.where(
    ...   (User.name == 'Jack') & (User.id >= 6)
    ... ).select(User.id)
    <SelectQuery "select user.id from user where user.name = 'Jack' and user.id >= '6'">
    >>> User.where(
    ...   (User.name == 'Jack') | (User.id >= 6)
    ... ).select(User.id)
    <SelectQuery "select user.id from user where user.name = 'Jack' or user.id >= '6'">
