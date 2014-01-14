.. _returns:

函数返回值
==========

.. Contents::

对于所有的查询(C, U, R, D), 它们执行后的返回值为:

- **C**:  插入的行的主键或者该模型类的实例

- **U**:  影响的行数

- **R**: ``SelectResult`` 对象

- **D**:  影响的行数

Create
-------

``Model.create`` 返回一个该模型类的实例::

    >>> User.create(name='jack')
    <models.User object at 0xb6f8dc4c>

``model.save`` 返回插入记录的主键::


    >>> user = User(name='jack')
    >>> user.save()
    7L

Update
-------

Update查询返回影响到的记录行数::

    >>> query = User.where(name='jack').update(email='jack@gmail.com')
    >>> query.execute()
    2L

``model.save`` 所执行的更新查询也返回影响的行数::

    >>> user = User.at(1),getone()
    >>> user.name = 'aNewName'
    >>> user.save()
    1L

Read
----

执行一个select查询返回 ``SelectResult object``::

    >>> results = User.where(name='jack').select().execute()
    >>> results
    <CURD.SelectResult object at 0xb6f8df6c>

Delete
------

执行一个delete查询返回删掉的行数::

    >>> user.destroy()
    1L
    >>> User.where(name='jack').delete().execute()
    4L
