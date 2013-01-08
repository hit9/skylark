.. include:: header.rst

Quick Start
===========

Simple Example
--------------

Codes works with virgo looks like

::

    from virgo import *

    Database.config(db="mydb", user="root", passwd="")


    class User(Model):
        name = Field()
        email = Field()

    user = User(name="Jack", email="Jack@github.com")

    user.save()

In this code, first we imported the virgo module.

Next we define a model:``User``, ``User`` has 3 fields:name, email and id.

(*Note:id is the default primary key*)

Then, we create an instance if model User.

Finally we insert one record into database by calling function ``save``
