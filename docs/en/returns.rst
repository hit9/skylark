.. _returns:

Return Values
=============

.. Contents::

For all queries (C, U, R, D), their executed returns are:

- **C**:  ``last row's id`` or ``Model instance``

- **U**:  ``rows affected``

- **R**: ``SelectResult object``

- **D**:  ``rows affected``

Here are examples:

Create
-------

``Model.create`` returns a ``Model instance``::

    >>> User.create(name='jack')
    <models.User object at 0xb6f8dc4c>

``model.save`` returns inserted row's id::


    >>> user = User(name='jack')
    >>> user.save()
    7L

Update
-------

Update queries return number of the rows affected::


    >>> query = User.where(name='jack').update(email='jack@gmail.com')
    >>> query.execute()
    2L

even queries from ``model.save``::

    >>> user = User.at(1),getone()
    >>> user.name = 'aNewName'
    >>> user.save()
    1L

Read
----

Return ``SelectResult object``::

    >>> results = User.where(name='jack').select().execute()
    >>> results
    <skylark.SelectResult object at 0xb6f8df6c>

And from ``SelectResult object``, we can fetch ``user``::

    >>> results.one()
    <models.User object at 0xb6f8dccc>


Delete
------

Return number of the rows deleted::


    >>> user.destroy()
    1L
    >>> User.where(name='jack').delete().execute()
    4L
