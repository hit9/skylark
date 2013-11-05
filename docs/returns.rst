.. _returns:

Return Values
=============

.. Contents::

For all queries (C, U, R, D), return values are:

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


    >>> User.where(name='jack').update(email='jack@gmail.com')
    2L

even queries from ``model.save``::

    >>> user = User[1]
    >>> user.name = 'aNewName'
    >>> user.save()
    1L

Read
----

Return ``SelectResult object``::

    >>> User.where(name='jack').select()
    <CURD.SelectResult object at 0xb6f8df6c>

And from ``SelectResult object``, we can fetch ``Model object``::

    >>> User.where(name='jack').select().fetchone()
    <models.User object at 0xb6f8dccc>


Delete
------

Return number of the rows deleted::

    
    >>> user.destroy()
    1L
    >>> User.where(name='jack').delete()
    4L
