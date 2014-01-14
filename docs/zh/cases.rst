.. _cases:

应用情景
========

.. Contents::

这部分包含一些使用CURD.py的场景。

条件性地插入
------------

比如，我们的会员管理系统只插入“新名字”::

    user = User(name='Jack')

    if user in User:
        return   # 拒绝
    else:
        user.save()  # 插入

分页
----

这是一个非常古老的编程任务， 当我们设计一个博客系统或者内容管理系统的时候
也许会碰到。如下的代码中假定每页含n条记录，取出的为第m页的记录::

    >>> query = Post.where(
    ...   is_published=True  # 仅仅取出已发布文章
    ... ).orderby(
    ...   Post.create_at, desc=True  # 最新发布文章居前边
    ... ).limit(
    ...   n, offset=n * (m-1)  # 限制条数
    ... ).select()

我们如何判断当前页面是否为第一页或者最后一页呢？

判断首页非常简单::

    >>> m == 1

但是判断最后一页需要对所有记录计数::

    >>> count = Post.count()
    >>> m * n >= count
    True  # 最后一页

注: 判断最后一页的部分，更严格地，需要对已发布的文章进行计数::

    >>> query = Post.where(is_published=True).select(Fn.count(Post.id))
    >>> result = query.execute()
    >>> row = result.fetchone()
    >>> count = row.count_of_id
    >>> m * n >= count
    True  # 最后一页

获取上一条或者下一条记录
------------------------

比如我们在创建一个博客，我们想要在一个文章页面标出这个文章的上一篇和下一篇文章
的链接。 假定这个文章在数据库中的id是4。

获取下一篇文章(在id>4的记录中取出id最小的就是下一条记录)::

    >>> query = Post.where(id=(
    ...   Post.where(Post.id > 4).select(Fn.min(Post.id))
    ... )).select(Post.id, Post.title)
    >>> query.sql
    "select post.title, post.id from post where post.id = (select min(post.id) from post where post.id > '4')"

获取上一篇文章(在id<4的记录中取出id最大的就是下一条记录)::

    >>> query = Post.where(id=(
    ...   Post.where(Post.id < 4).select(Fn.max(Post.id))
    ... )).select(Post.id, Post.title)
    >>> query.sql
    "select post.title, post.id from post where post.id = (select max(post.id) from post where post.id < '4')"

如果我们想在一次查询中就得到这上一篇和下一篇的话，我们可以使用 ``in`` 操作符::

    >>> query = Post.where(Post.id._in(
    ...   Post.where(Post.id > 4).select(Fn.min(Post.id)),
    ...   Post.where(Post.id < 4).select(Fn.max(Post.id)),
    ... )).select(Post.id, Post.title)
    >>> [(post.id, post.title) for post in query]
    [(3L, u'Python GOOD'), (5L, u'Happy dog')]


另一种方法是使用 ``limit``, 如下是获取下一篇文章的代码(在id>4的所有记录中按照id排序并限制取1条即得下一条记录)::

    >>> query = Post.where(Post.id > 4).orderby(Post.id).limit(1).select(Post.title, Post.id)
    >>> query.sql
    "select post.title, post.id from post where post.id > '4' order by post.id limit 1 "

----------


欢迎补充， 请提到issue: https://github.com/hit9/CURD.py/issues
