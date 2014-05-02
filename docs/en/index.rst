.. _index:

Overview
========

A nice micro orm for python, mysql only. (Original named CURD.py).

Release: v\ |version| - Beta (:ref:`Installation <install>`) 

Tests status:

.. image:: https://travis-ci.org/hit9/skylark.png?branch=master

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
<https://github.com/hit9/skylark/tree/master/docs/sample>`_.


.. _requirements:

Requirements
------------

* Python >= 2.6 or >= 3.3

* `MySQLdb(MySQL-python) <https://pypi.python.org/pypi/MySQL-python>`_ or `PyMySQL <https://github.com/PyMySQL/PyMySQL>`_

.. _install:

Installation
------------

::

    $ pip install skylark

Plat
----

Python2.6+ or 3.3+, OS Independent

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
