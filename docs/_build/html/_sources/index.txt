.. include:: header.rst

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

    from models import *

    user = User(nam="Liming", email="Liming@github.com")
    user.save()

    user = User.where(name="Liming").select().fetchone() 
    print user.email

    for post,user in (Post & User).select().fetchall():
        print "user %s post's name is %s" %(user.name, post.name)

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

License
-------

BSD_. Short and sweet.

.. _BSD: license.html
