.. _quickstart:

.. include:: header.rst

Quick Start
===========

Simple Example
--------------

Codes works with virgo looks like

.. literalinclude:: code/QuickStart/example.py

1. In this code, first we imported the virgo module and configure the Database.

2. Next we define a model:``User``, which has 3 fields:``name``, ``email`` and ``id`` (*Note:id is the default primary key*)

3. Then, we create an instance if model ``User``.

4. Finally we insert one record into database by calling function ``save``

Database Configuration
----------------------

``db``, ``user``, ``passwd`` are required:

::

    Database.config(db="mydb", user="root", passwd="")


For more options, see :ref:`Database.config`


Define Model
------------

example:

::

    class User(Model):
        name = Field()
        email = Field()
        # default primarykey is id, to figure out primarykey : 
        # myid = PrimaryKey()


All models are inherited from Model.
virgo regards the lower case of model's classname as its table's name
