Welcome to virgo's world !
==========================

Simple and easy to use ORM module for MySQL Database and Python 2 

Overview_ // QuickStart_ // Github_ // Issues_  

.. _Overview: index.html
.. _QuickStart: QuickStart.html
.. _Github: http://github.com/hit9/virgo
.. _Issues: https://github.com/hit9/virgo/issues

Overview
********

Install
-------

Install from pypi::

    pip install virgo

Sample Code
-----------

models.py ::

    from virgo import *

    Database.config(db="mydb", user="root", passwd="123456")

    class User(Model):
        name = Field()
        email = Field()

    class Post(Model):
        post_id = PrimaryKey()
        name = Field()
        user_id = ForeignKey(User.id)

main.py ::

    user = User(name = "Liming", email = "Liming@github.com")
    user.save()

    user = User.where(name = "Liming").select().fetchone() 
    print user.email

    for post,user in (Post & Post).select().fetchall():
        print "user:%s post's name:%s" %(user.name, post.name)

Run Tests
---------

Clone virgo from Github_ ,and then::

    cd tests/
    nosetests

Build Status
------------

.. Image:: https://api.travis-ci.org/hit9/virgo.png

Read Document
-------------

Clone virgo from Github_ ,and then::

    cd docs/
    make html
