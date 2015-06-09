.. _index:

Overview
========

Nice micro python orm for mysql and sqlite3. (Original named CURD.py).

Release: v\ |version| - Beta (:ref:`Installation <install>`)

Build status:

.. image:: https://travis-ci.org/hit9/skylark.png?branch=master

.. Contents::

.. _Sample:

Sample
------

::

    >>> from models import User
    >>> user = User(name='Tom', email='tom@gmail.com')
    >>> user.save()  # insert
    1
    >>> user.email = 'tom@github.com'
    >>> user.save()  # update
    1
    >>> [user.name for user in User.select()]  # select
    [u'Tom']
    >>> query = User.where(name='Tom').delete()
    >>> query.execute()  # delete
    1
    >>> user = User.create(name='Kate', email='kate@gmail.com')  # another insert
    >>> user
    {'email': 'kate@gmail.com', 'name': 'Kate', 'id': 2}
    >>> user.destroy()  # another delete
    1

More sample codes `here
<https://github.com/hit9/skylark/tree/master/sample>`_

.. _requirements:

Requirements
------------

* Python >= 2.6 or >= 3.3

* For mysql users: `MySQLdb(MySQL-python) <https://pypi.python.org/pypi/MySQL-python>`_ or `PyMySQL <https://github.com/PyMySQL/PyMySQL>`_

.. _install:

Installation
------------

::

    $ pip install skylark


Documentation
-------------

.. toctree::
    :maxdepth: 2
    :numbered:

    quickstart
    models
    database
    returns
    operators
    tips
    exceptions
    apps
