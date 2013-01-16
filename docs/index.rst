Overview
********

Install
-------

::
    pip install virgo


Note:virgo works with Python 2.x(tested: 2.5, 2.6, 2.7)

Sample Code
-----------

::

    >>> user = User(name="Jack", email = "Jack@gmail.com") 
    >>> user.save() 
    1L
    >>> user = User.at(1).select().fetchone() 
    >>> user.name, user.email 
    (u'Jack', u'Jack@gmail.com')
    >>> Post.create(name="Hello World!",user_id=1) 
    <models.Post object at 0x8ec492c>
    >>> for post, user in (Post & User).select().fetchall(): 
    ...     print user.name, post.name
    ...  
    Jack Hello World!

Run Tests
---------

Clone virgo from Github_ ,and then::

    cd tests/
    nosetests

Build Status
------------

.. Image:: https://api.travis-ci.org/hit9/virgo.png?branch=master

Read Document
-------------

Clone virgo from Github_ ,and then::

    cd docs/
    make html

License
-------

The :ref:`license` :BSD.Short and sweet.

.. _Github: https://github.com/hit9/virgo
