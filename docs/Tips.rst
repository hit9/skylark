.. _tips:

CURD.py Tips
============

Use destroy() wisely
--------------------

To delete one record.

::
    
    User.at(2).delete()

is better than ::

    user = User.at(2).select().fetchone()
    user.destroy() # this queried 2 times


Only 7 functions query db
-------------------------

they are: 

::

    select()
    update()
    create()
    delete()
    save()
    destroy()
    model_instance in Model  # actually, it calls function - select()

Test if one record is in the table(Sugar)
-----------------------------------------

if someone in database called 'Jack'? ::

    user = User(name="Jack")
    if user in User:
        print "Yes!"

mix your methods into Model
---------------------------

To get the user whose id is 3 (suppose id is the primary key)::

    user = User.at(3).select().fetchone()

Too long ?

Let's define a shorter one: ``get(key)`` ::

    @classmethod
    def get(cls, key):
        return cls.at(key).select().fetchone()
    Model.get = get

after this code, you can do the same thing like this::

    user = User.get(3)


Or more shorter::


    def getitem(model,index):
        return model.at(index).select().fetchone()
    MetaModel.__getitem__=getitem

use ``[]`` to do this::

    user=User[1]

Put all models in one script in your app
----------------------------------------

in models' file: models.py:

.. literalinclude:: ../sample/models.py

and in other scripts : ::

    from models import User
    User.select()  # etc..
