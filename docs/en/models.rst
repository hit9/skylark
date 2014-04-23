.. _model-definition:

Model Definition
=================

A table in mysql corresponds to a class in Python, i.e. we create a
table ``comment``:

.. code-block:: sql

    mysql> create table comment(
      id int primary key auto_increment,
      content text,
      create_at datetime,
      user_id int,
      foreign key(user_id) references user(id)
    )engine=innodb default charset=utf8;


this table looks like:

.. code-block:: sql

    +-----------+----------+------+-----+---------+----------------+
    | Field     | Type     | Null | Key | Default | Extra          |
    +-----------+----------+------+-----+---------+----------------+
    | id        | int(11)  | NO   | PRI | NULL    | auto_increment |
    | content   | text     | YES  |     | NULL    |                |
    | create_at | datetime | YES  |     | NULL    |                |
    | user_id   | int(11)  | YES  | MUL | NULL    |                |
    +-----------+----------+------+-----+---------+----------------+


We should define its model class in Python like this::

    from CURD import Model, Field, ForeignKey

    class Comment(Model):
        content = Field()
        create_at = Field()
        user_id = ForeignKey(User.id)

We need to create tables by hand and then define their model classes in Python.

In code above, ``id`` is the default primarykey, ``user_id`` is a foreignkey references ``user.id``.
By default, we take classname's "snake case" as its table's name. And for models like ``MyTable`` (Pascal naming style)::

    class MyTable(Model):
        pass

its table's name will be ``my_table`` . If your table dont meet this rule, you can also customize the table name::

    class SomeModel(Model):
        table_name = 'my_custom_table_name'

And, better to define all models in one module.
