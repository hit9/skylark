.. _index:

CURD - Tiny Python ORM for MySQL
================================

Release: v\ |version| - Beta (:ref:`Installation <install>`) 

Tests status:

.. image:: https://travis-ci.org/hit9/CURD.py.png?branch=master

CURD.py is a tiny orm for mysql database, written in Python.

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

Python2 (2.6+), OS Independent

Documentaion
------------

.. toctree::
    :maxdepth: 3
    :numbered:

    quickstart
    models
    returns
    types
    database
    apps
    tips
    cases
    exceptions
    faq
    changes
