.. _Model:

Model
=====

::

    class Model(*fldAssign, **data):

Models are mapped to tables in database. Each model should inherit from class ``Model``.

example of making an instance of model `User`

**Parameters**: 

- **data** : key:value pairs of model attributes

- **fldAssign** : ``Field instance == value`` expressions

example:

::

    class User(Model):
        myid=PrimaryKey()
        name = Field()
        email = Field()

    user=User(name="mark",email="mark@gmail.com")

.. _Model.tablename:

Model.table_name
----------------

return model's tablename.(lowercase of model's classname)

Example:

::

    >>> User.table_name
    'user'

.. _Model.primarykey:

Model.primarykey
----------------

return model's primary key

::
    
    >>> User.primarykey 
    <virgo.PrimaryKey object at 0x9e9558c>

.. _Model.create:
    
Model.create
------------

create one record.

::

     classmethod Model.create(*fldAssign,**data)

**Parameters**: 

- **data** : key:value pairs of model attributes

- **fldAssign** : ``Field instance == value`` expressions

**Return**: An instance of the model class.

example:

::

    >>> User.create(name="Jack",email="Jack@abc.com")
    <models.User object at 0x9e98b0c>
    >>> User.create(User.name == "Jack", User.email == "Jack@abc.com")
    <models.User object at 0x9fbf04c>

.. _Model.update:

Model.update
------------

update record(s)


::

    classmethod Model.update(*fldAssign,**data)


**Parameters**: 

- **data** : key:value pairs of model attributes

- **fldAssign** : ``Field instance == value`` expressions

**Return**: affected rows number.

example:

::

    >>> User.where(User.name=="Jack").update(User.name=="Mick") 
    3

.. _Model.select:

Model.select
-------------

select record(s) ::

    classmethod select(*fields)

**Parameters**: 

- **fields**:Field instances to select

- **Return**: SelectResult instance

About SelectResult, simply to say, there are 2 methods for its instance:

* fetchall(): return a generator of model instances

* fetchone(): return only one model instance.

example:

::

    >>> selects=User.where(User.name=="Mick").select(User.email)
    >>> for user in selects.fetchall(): 
    ...     print user.id, user.email
    ...  
    1 Jack@github.com
    5 Jack@abc.com
    6 Jack@abc.com

If no fields given, virgo selects all fields:

::

    >>> user=User.at(1).select().fetchone() 
    >>> user.data 
    {'id': 1L, 'email': u'Jack@github.com', 'name': u'Mick'}


.. _Model.delete:

Model.delete
------------

delete record(s)

::

    classmethod delete()

**Return**:deleted rows number.

example:

::

    >>> User.where(User.id > 6).delete()
    1


.. _Model.where:

Model.where
-----------

::

    classmethod where(*expressions, **data)


**Parameters**: 

- **expressions**: expressions like ``User.id > 10``, instance of class Expr

- **data**: attributes - key:value pairs of model attributes

**Return**: model

example:

::
    
    >>> User.where(User.name=="Mick") 
    <class 'models.User'>
    >>> User.where(User.name=="Mick").select() 
    <virgo.SelectResult object at 0x9e9560c>

Expessions will be joined with "and" in SQL.
