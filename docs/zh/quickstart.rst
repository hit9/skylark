.. _quickstart:

快速上手
========

.. Contents::

.. _DatabaseConfig:

数据库配置
----------
我们首先需要通过配置Database来告诉CURD.py怎样连接数据库,
``db``, ``user``, ``passwd`` 是必需项::

    Database.config(db='mydb', user='root', passwd='')

当你执行查询的时候CURD.py会自动建立到mysql的数据库连接，不必手动连接。

更为详细的配置项见 :ref:`db_configuration` .

.. _DefineModel:

模型定义
--------

::

    class User(Model):
        name = Field()
        email = Field()
        # 默认主键: `id`, 指明主键:
        #   myid = PrimaryKey()

在上面的代码中我们定义了一个模型 ``User``, 它有3个字段: ``name``, ``email`` 和 ``id`` (``'id'`` 是缺省主键)。

所有的模型类应当继承自 ``Model`` 。

我们可以指明一个模型类的对应表名::

    class SomeModel(Model):
        table_name = 'tablename_of_somemodel'

缺省情况下，我们使用模型类的全小写作为表名, 比如::

    class User(Model):  # 对应的表名: 'user'
        pass

    class SomeModel(Model):  # 对应的表名: 'some_model'
        pass


最好把所有的模型放入同一个Py文件中，比如叫做 ``models.py``:

.. _two_models:

.. literalinclude:: ../sample/models.py

注意以下:

* 你需要手动创建数据库表, CURD.py没有类似 ``create_tables`` 的建表方法.

* 以上两个数据库表的sql语句定义在 `这里 <https://github.com/hit9/CURD.py/blob/master/tests/tables.sql>`_ 。

.. _Create:

Create
------

把"Jack"添加到数据库中::

    >>> from models import User
    >>> User.create(name='jack', email='jack@gmail.com')
    <models.User object at 0x8942acc>  # User object

``create`` 方法返回了一个User对象.

或者使用 ``save`` 方法::

    >>> user = User()
    >>> user.name = 'jack'
    >>> user.email = 'jack@gmail.com'
    >>> user.save()
    1L  # 插入列的主键值

这也等价于::

    >>> user = User(name='jack',email='jack@gmail.com')
    >>> user.save()
    2L

.. _Update:

Update
------

很简单， 只要 ``save``::

    >>> user.name = 'Any'
    >>> user.save()  # return 0 for failure,else success
    1L  # 影响了1行

或者使用 ``update`` 方法 ::

    >>> query = User.at(2).update(name='Join')
    >>> query
    <UpdateQuery "update user set user.name = 'Join' where user.id = '2'">
    >>> query.execute()  # 执行这个query
    1L

``update`` 方法返回一个 ``UpdateQuery`` 对象， **每种查询对象都有execute方法来执行这个查询** 。

另外，上面代码中 ``User.at(id_value)`` 等价于 ``User.where(User.id == id_value)`` , 都返回类 ``User`` 。

.. _Read:

Read
----

例子::

    >>> query = User.where(name='Join').select()
    >>> query
    <SelectQuery "select user.id, user.name, user.email from user where user.name = 'Join'">
    >>> result = query.execute()
    >>> for user in result.fetchall():
    ...   print user.name, user.email
    ...
    Join jack@gmail.com

其中， ``name="Any"`` 也可以替换为 ``User.name == "Any"``.

当我们迭代一个SelectQuery对象的时候，CURD.py会执行这个SelectQuery对象::

    >>> query = User.where(name='Join').select()
    >>> for user in User.select():
    ...   print user.name, user.email
    ...
    jack jack@gmail.com
    Join jack@gmail.com

如果我们按照主键来获取记录，可以使用 ``Model.at(var)``::

    >>> query = User.at(1).select()
    >>> query
    <SelectQuery "select user.id, user.name, user.email from user where user.id = '1'">
    >>> result = query.execute()
    >>> user = result.fetchone()
    >>> user.name, user.id
    (u'jack', 1L)

select
''''''

``select`` 方法可以构造一个select查询::

    >>> User.where(User.id > 4).select(User.name)
    <SelectQuery "select t_user.name from t_user where t_user.id > '4'">

``select`` 方法的参数是我们关心的字段，方法返回一个 ``SelectQuery`` 对象。

我们需要查询所有的用户::

    User.select()

我们只关心id大于5的用户的名字::

    User.where(User.id > 5).select(User.name)


SelectResult对象
''''''''''''''''

当我们执行SelectQuery对象后会得到一个查询结果对象
(``SelectResult object``)::

    >>> query = User.select()
    >>> results = query.execute()
    >>> results
    <CURD.SelectResult object at 0x9c62b4c>

该对象有两个方法可以抓取结果:

- ``fetchone()``: 一次抓取一条记录::

     >>> results.fetchone()
     <models.User object at 0xb703148c>

- ``fetchall()``: 一次抓取全部记录::

     >>> results = query.execute()
     >>> results.fetchall()
     <generator object fetchall at 0x9c61644>

该对象还有一个属性 ``count`` ，它记录着结果的条数::

     >>> results.count
     9L # 查询到了2条

快捷查询
''''''''

有4个方法来快速地执行select查询:

- ``findone``, 找到符合条件的一条记录::

     >>> user = User.findone(name='Join')  # <=> User.where(name='Join').select().execute().fetchone()
     >>> user.id
     2L

- ``findall``, 找到所有符合条件的记录::

     >>> users = User.findall(User.id > 0, name='Join') # <=> User.where(User.id > 0 name='Join').select().execute().fetchall()
     >>> [user.name for user in users]
     [u'Join']

- ``getone``, 取出一条记录::

     >>> user = User.at(2).getone() # <=> User.where(id=2).select().execute().fetchone()
     >>> user.name
     u'Join'

- ``getall``, 取出全部记录::

     >>> users = User.where(User.id > 4).getall()
     >>> [user.name for user in users]
     [u'jack', u'tom', u'tom', u'tom', u'tom', u'jack', u'ss']

.. _Delete:

Delete
------

删除一个对象对应的数据库记录::

    >>> user.destroy()
    1L  # 删除的行数

或者使用 ``delete`` 构造一个 ``DeleteQuery``, 然后执行它::

    >>> query = User.at(1).delete()
    >>> query
    <DeleteQuery "delete user from user where user.id = '1'">
    >>> query.execute()
    1L  # 删除的行数

两个方法都返回影响的记录条数。

.. _Where:

Where
-----

``where`` 方法似乎很神奇, 它用来指明筛选条件::

    Model.where(*expressions, **data)  # 返回当前模型类

Where使用示例
''''''''''''''

::

    >>> query = User.where(name='Jack').select()
    >>> query.sql
    "select user.name, user.email, user.id from user where user.name = 'Jack'"

    >>> query = User.where(User.id.between(3,6)).select()
    >>> query.sql
    "select user.id, user.name, user.email from user where user.id between '3' and '6'"

    >>> query = User.where(User.name.like('%sample%')).select()
    >>> query.sql
    "select user.name, user.email, user.id from user where user.name like '%sample%'"

where的参数应该是一个或者多个"表达式对象"， 所有支持的"表达式"在 :ref:`expressions`

子查询
''''''

一个使用操作符 ``_in`` 的子查询例子::

    >>> query = User.where(User.id._in(
    ...   Post.select(Post.user_id)
    ... )).select()
    >>> query.sql
    'select user.id, user.name, user.email from user where user.id in ((select post.user_id from post))'
    >>> [(user.id, user.name) for user in query]  # run this query
    [(3L, u'Join'), (5L, u'Amy')]

注意: 目前CURD.py只支持操作符中的子查询，暂不支持select中的子查询等。

Group By
---------

原型::

    groupby(*Field Objects)

示例::

    >>> query = User.groupby(User.name).select(User.id, User.name)
    >>> query.sql
    'select user.name, user.id from user group by user.name'

Having
------

原型::

    having(*Expression Objects)

示例::

    >>> query = User.groupby(User.name).having(Fn.count(User.id) > 3).select(User.id, User.name)
    >>> query.sql
    "select user.name, user.id from user group by user.name having count(user.id) > '3'"

.. _orderby:

Order By
--------

原型::

    orderby(Field Object, desc=False)

示例::

    >>> query = User.where(User.id < 5).orderby(User.id, desc=True).select()
    >>> query.sql
    "select user.id, user.name, user.email from user where user.id < '5' order by user.id desc "

Limit
-----

原型::

    limit(rows, offset=None)

示例::

    >>> query = User.limit(2, offset=1).select()
    >>> query.sql
    'select user.id, user.name, user.email from user limit 1, 2 '

Distinct
--------

原型::

    distinct()

示例::

    >>> for user in User.distinct().select(User.name):
    ...   user.name
    ...
    u'jack'
    u'tom'

注意: distinct方法可能会在未来的版本中去除， 而使用其作为 field 的前缀修饰。

X在数据库中吗
-------------

::

    >>> jack = User(name='Jack')
    >>> jack in User
    True  # 数据库中确有一个叫做'Jack'的用户

.. _JoinModel:

联合模型
---------

我们在models.py中定义了 :ref:`两个模型 <two_models>` : ``User``, ``Post``

.. literalinclude:: ../sample/models.py

现在我们要做两表联合查询，看下面的语法::

    >>> Post & User
    <CURD.JoinModel object at 0xb76f292c>


注: 不能使用 ``User & Post`` 是因为 ``&`` 操作符是有方向的，它从原模型指向外模型(即指向外表的主键)。

以下是使用示例。


我们看看哪个用户写了哪个文章::

    >>> for post, user in (Post & User).select():
    ...   print '%s wrote this post: "%s"' % (user.name, post.name)
    ...
    Jack wrote this post: "Hello wolrd!"
    Amy wrote this post: "I love Python"
    Join wrote this post: "I love GitHub"
    Join wrote this post: "Never Give Up"

当然，联合模型是拥有 ``where``, ``orderby``, ``delete`` 等方法的， 像单个模型类一样。

比如，我们来删除Jack写的文章::

    >>> query = (Post & User).where(User.name == 'Jack').delete(Post)
    >>> query
    <DeleteQuery "delete post from post, user where user.name = 'Jack' and post.user_id = user.id">
    >>> query.execute()
    1L

SQL函数
-------

一个例子，对数据库中的用户进行计数::

    >>> from CURD import Fn
    >>> query = User.select(Fn.count(User.id))
    >>> query
    <SelectQuery 'select count(user.id) from user'>
    >>> result = query.execute()
    >>> user = result.fetchone()
    >>> user.count_of_id
    4L

所有的函数都是作为属性绑定在 ``Fn`` 上的。上面的代码中我们使用了 ``Fn.count`` 来创建一个 ``Function`` 对象::

    >>> Fn.count(User.id)
    <Function 'count(user.id)'>


随后使用 ``user.count_of_id`` 来获取记录的数量。

目前， CURD.py 仅仅支持5个合计函数:

- ``count``
- ``sum``
- ``max``
- ``min``
- ``avg``

和两个scalar函数:

- ``ucase``
- ``lcase``

所有的函数都是像上面的例子中那样使用的，这里是一个例子(获取所有用户的大写名字)::

    >>> [user.ucase_of_name for user in  User.select(Fn.ucase(User.name))]
    [u'JOIN', u'JACK', u'AMY', u'JACK']


合计函数的快捷方式
''''''''''''''''''

在大多数情况下，在同一次查询中我们不混合函数和字段，比如我们仅仅需要一个表的行数。

我们可以这样获取::

    >>> User.count()
    4L

类似的，所有的合计函数都有这种快捷做法::

    >>> User.count()
    4L
    >>> User.max(User.id)
    6L
    >>> User.min(User.id)
    3L
    >>> User.sum(User.id)
    Decimal('18')
    >>> User.avg(User.id)
    Decimal('4.5000')
