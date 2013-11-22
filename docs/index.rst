.. _index:

CURD - Tiny ORM for MySQL
=========================

Release: v\ |version| (:ref:`Installation <install>`) 

**NOTE**: version 0.3.0 has a lot of **Not-Backward-Compatible** changes
compared to version 0.2.5.

Tests status:

.. image:: https://travis-ci.org/hit9/CURD.py.png?branch=dev

CURD.py is a tiny orm for mysql database, written in Python.

.. Contents::

.. _SimpleExample:

Sample
------

Codes works with CURD.py looks like

.. literalinclude:: sample/sample.py

1. In this code, first we imported the ``CURD`` module and configure the Database class.

2. Next we define a model: ``User``, which has 3 fields:``name``, ``email`` and ``id`` (*Note:id is the default primary key*)

3. Then, we create an instance of ``User``.

4. Finally we insert one record into database by calling method ``save``

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

- Create

- Update

- Read

- Delete

- Multiple Tables

Plat
----

Python 2.6+, OS Independent

Documentaion
------------

.. toctree::
    :maxdepth: 2
    :numbered:

    quickstart
    tips
    returns
    types
    faq
