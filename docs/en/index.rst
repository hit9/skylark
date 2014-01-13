.. _index:

CURD - Tiny Python ORM for MySQL
================================

Release: v\ |version| (:ref:`Installation <install>`) 


.. **NOTE**: version 0.3.0 has a lot of **Not-Backward-Compatible** changes
.. compared to version 0.2.5.

Tests status:

.. image:: https://travis-ci.org/hit9/CURD.py.png?branch=dev

CURD.py is a tiny orm for mysql database, written in Python.

**NOTICE**: CURD.py may not be stable before version 1.0

.. Contents::

.. _SimpleExample:

Sample
------

::

    >>> from models import User
    >>> user = User(name='Tom', email='tom@gmail.com')
    >>> user.save()  # insert
    1L
    >>> user.email = 'tom@github.com'
    >>> user.save()  # update
    1L
    >>> [user.name for user in User.select()]  # select
    [u'Tom']
    >>> query = User.where(name='Tom').delete()
    >>> query.execute()  # delete
    1L
    >>> user = User.create(name='Kate', email='kate@gmail.com')  # another insert
    >>> user.data
    {'email': 'kate@gmail.com', 'name': 'Kate', 'id': 2L}
    >>> user.destroy()  # another delete
    1L

More sample codes `here
<https://github.com/hit9/CURD.py/tree/master/docs/sample>`_.

.. _install:

Installation
------------

::

    $ pip install CURD.py


Supports
--------

CURD.py only supports 4 types of queries: C, U, R, D, responsing to its name.

- :ref:`Create` 

- :ref:`Update`

- :ref:`Read`

- :ref:`Delete`

Plat
----

Python2(2.6+), OS Independent

Documentaion
------------

.. toctree::
    :maxdepth: 3
    :numbered:

    quickstart
    returns
    types
    tips
    cases
    database
    exceptions
    faq
    changes
