.. _model-definition:

模型定义
========

数据库中的表在Python中对应为一个类。


比如我们建立一个表 ``comment``

.. code-block:: sql

    mysql> create table comment(
      id int primary key auto_increment,
      content text, 
      create_at datetime,
      user_id int,
      foreign key(user_id) references user(id)
    )engine=innodb default charset=utf8;


也就是这样的一个表

.. code-block:: sql

    +-----------+----------+------+-----+---------+----------------+
    | Field     | Type     | Null | Key | Default | Extra          |
    +-----------+----------+------+-----+---------+----------------+
    | id        | int(11)  | NO   | PRI | NULL    | auto_increment |
    | content   | text     | YES  |     | NULL    |                |
    | create_at | datetime | YES  |     | NULL    |                |
    | user_id   | int(11)  | YES  | MUL | NULL    |                |
    +-----------+----------+------+-----+---------+----------------+


对应地，我们在Python代码应该建立如下的模型类::

    from CURD import Model, Field, ForeignKey

    class Comment(Model):
        content = Field()
        create_at = Field()
        user_id = ForeignKey(User.id)

在使用CURD.py的时候需要自己建立数据库表，然后写出对应的模型类。

如上的代码中，id是默认情况下的主键字段，user_id被声明为引用user.id的外键。默认地，采用模型类
名字的全小写当作该模型对应的表的表名。对于类似 ``MyTable`` 这样的两个或多个大写(帕斯卡命名风格的)的模型::

    class MyTable(Model):
        pass

它对应的表名为 ``my_table`` 。如果你的表名不符合这种规则，那么可以主动告诉CURD.py一个模型的表名是什么::

    class SomeModel(Model):
        table_name = 'my_custom_table_name'

我们建议把所有的模型类都定义在同一个模块里。
