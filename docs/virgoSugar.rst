.. _virgoSugar:

virgoSugar
==========

I wrote some syntax sugar for virgo, to use them::

    from virgoSugar import *

But, be careful to use the sugar.

Get Item
--------

example::

    >>> user=User[2] 
    >>> user.name 
    u'Amy'

It's just a quick way to run this line codes::
   
    user=User.where(User.primarykey == 2).select().fetchone()

Slice
-----

example::

    >>> users=User[1:3] 
    >>> for user in users: 
    ...     print user.id,user.name
    ...  
    1 Jack
    2 Amy
    3 James

It's just a quick way of::

    users=User.where(User.primarykey >= start, User.primarykey <= end)

And, ``User[start:]``, ``User[:end]``, ``User[:]`` also work::

    >>> User[:3] 
    <generator object fetchall at 0x8a5f9dc>
    >>> User[1:]
    <generator object fetchall at 0x8a5f9b4>
    >>> User[:]
    <generator object fetchall at 0x8a5fa04>
