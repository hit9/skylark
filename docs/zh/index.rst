.. _index:

CURD.py - Python的MySQL微型ORM
===============================

最新发布: v\ |version| (:ref:`安装 <install>`) 


测试状态:

.. image:: https://travis-ci.org/hit9/CURD.py.png?branch=dev

CURD.py是一个使用Python编写的小巧的MySQL ORM.

`Englinsh version documentation <http://curdpy.readthedocs.org/>`_

**注意**: CURD.py在v1.0版本之前可能会不稳定。

.. Contents::

.. _SimpleExample:

示例
----

::

    >>> from models import User
    >>> user = User(name='Tom', email='tom@gmail.com')
    >>> user.save()  # 插入
    1L
    >>> user.email = 'tom@github.com'
    >>> user.save()  # 更新
    1L
    >>> [user.name for user in User.select()]  # select
    [u'Tom']
    >>> query = User.where(name='Tom').delete()
    >>> query.execute()  # 删除
    1L
    >>> user = User.create(name='Kate', email='kate@gmail.com')  # 另一种插入
    >>> user.data
    {'email': 'kate@gmail.com', 'name': 'Kate', 'id': 2L}
    >>> user.destroy()  # 另一种删除
    1L


更多的例子见 `这里 <https://github.com/hit9/CURD.py/tree/master/docs/sample>`_

.. _install:


安装
----

::

    $ pip install CURD.py


支持
----

CURD.py只支持4种查询: C, U, R, D, 呼应它的名字。


- :ref:`Create` 

- :ref:`Update`

- :ref:`Read`

- :ref:`Delete`

平台需求
--------

Python2(2.6+), 跨操作系统

文档
----

.. toctree::
    :maxdepth: 3
    :numbered:

    quickstart
    models
    returns
    types
    database
    apps
    tips
    cases
    exceptions
    faq
    changes
