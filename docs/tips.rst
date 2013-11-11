.. _tips:

Some Tips
=========

.. Contents::

Use destroy() wisely
--------------------

To delete one record.

::

    User.at(2).delete()

is better than ::

    user = User.at(2).getone()
    user.destroy()  # this queried 2 times

The same tip with ``update``.


Test whether an except record is in the table
---------------------------------------------

Is there someone called 'Jack' in database? ::

    jack = User(name='Jack')
    if jack in User:
        print "Yes!"

mix your methods into Model
---------------------------

To get the user whose id is 3 (suppose id is the primary key)::

    user = User.at(3).getone()

Too long ?

A shorter one::

    def getitem(model,index):
        return model.at(index).getone()
    MetaModel.__getitem__ = getitem

use ``[]`` to do this::

    user=User[1]

Put all models in one script in your app
----------------------------------------

in models' file: models.py:

.. literalinclude:: sample/models.py

and in other scripts : ::

    from models import User
    query = User.select()  # etc..
