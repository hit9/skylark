.. _model-definition:

Model Definition
=================

A table in database corresponds to a class in Python, we call it a model.

An example to define a model class::

    from skylark import Model, Field, ForeignKey

    class Comment(Model):
        content = Field()
        create_at = Field()
        user_id = ForeignKey(User.id)

In code above, ``id`` is the default primarykey,
``user_id`` is a foreignkey references ``user.id``. 

Table Name
-----------

By default, we take classname's “snake case”, as its table's name::

    class User(Model):  # table_name: 'user'
        pass

    class CuteCat(Model):  # table_name: 'cute_cat'
        pass


If your table dont meet this rule, you can also customize the table name::

    class User(Model):  # table_name: 'custom_name'
        table_name = 'custom_name'

Table Prefix
------------

Since v0.9.0, ``table_prefix`` is supported::

    class User(Model):  # table_name: 't_user'
        table_prefix = 't_'

    class User(Model):  # table_name: 't_custom_name'
        table_prefix = 't_'
        table_name = 'custom_name'


And we can share table prefix between all models::

    class BaseModel(Model):
        table_prefix = 't_'

    class User(BaseModel):  # table_name: 't_user'
        pass

    class Post(BaseModel):  # table_name: 't_post'
        pass
