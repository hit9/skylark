.. _where:

Where Clause
=============

.. Contents::

The method ``where()`` seems to be magic::

    Model.where(*lst, **dct)

The ``lst`` should be expressions, the ``dct`` will convert to expressions at
last.

Expression
-----------

An expression is made up of ``left``, ``right``, and an ``operator``,
e.g. ::

    User.name == 'Jack'

The ``left`` is always a ``Field object``, and the ``right`` is always
a ``str``, ``number`` .etc.

Mapping to SQL
---------------

Here are some examples to show how are the expressions mapping to SQL strings::

    User.name == 'Jack'
    =>  user.name = 'Jack'

    (User.name == 'Jack') & (User.id == 2)
    =>  user.name = 'Jack' and user.id = 1

    (User.name == 'Jack') | (User.id == 1)
    =>  user.name = 'Jack' or user.id = 1

    User.name.like('%any%')
    =>  user.name like '%any%'

    ....


As arguments of ``where(*expressions)``, the expressions are in ``and`` relations::

    # this line code
    User.where(User.name == 'Jack', User.id == 3)

    # is the same with:
    User.where((User.name == 'Jack') & (User.id == 3))

    # also the same with:
    User.where(name='Jack', id=3)


Supported Operators
-------------------

All operators mappings are here::

    Expression          SQL String

    field < value   =>  "field < value"
    field <= value  =>  "field <= value"
    field > value   =>  "field > value"
    field >= value  =>  "field >= value"
    field == value  =>  "field = value"
    field != value  =>  "field <> value"
    field + value   =>  "field + value"
    field.like(value) => "field like value"
    field._in(v1, v2, ..) => "field in (v1, v2, ..)"
    field.between(v1, v2) => "field between v1 and v2"

    expression & expression => "expression and expression"
    expression | expression => "expression or expression"
