.. _cases:

Use Cases
=========

.. Contents::

This part contains some cases using skylark, hope this help you :)

Conditionally Insertion
-----------------------

For instance, our membership management system only accepts fresh names::

    user = User(name='Jack')
    
    if user in User:
      return   # refuse
    else:
      user.save()  # insert

Pagination
----------

This is an old old old programming task::

    >>> query = Post.where(
    ...   is_published=True  # Select published post only
    ... ).orderby(
    ...   Post.create_at, desc=True  # Show recent created posts
    ... ).limit(
    ...   n, offset=n * (m-1)  # Get n rows at offset (n*(m-1))
    ... ).select()

the code seems to be very long :D

But, how do we test if the current request page is the first/last page?

To test if it's the first page is easy::

    >>> m == 1

but to test if it's the last page needs the total rows count of table ``post``::

    >>> post_total_count = Post.count()
    >>> m * n >= post_total_count
    True  # Yes, the last page

Get next/previous record
------------------------

We are building a blog using skylark, and we want to display
next/previous article links on each article's page.

Suppose the current post's id is 4.

To get next post::

    >>> query = Post.where(id=(
    ...   Post.where(Post.id > 4).select(fn.min(Post.id))
    ... )).select(Post.id, Post.title)
    >>> query.sql
    "select post.title, post.id from post where post.id = (select min(post.id) from post where post.id > '4')"

To get previous post::

    >>> query = Post.where(id=(                                                                                                             
    ...   Post.where(Post.id < 4).select(fn.max(Post.id))                                                                                   
    ... )).select(Post.id, Post.title)
    >>> query.sql
    "select post.title, post.id from post where post.id = (select max(post.id) from post where post.id < '4')"

If you want to get them in only one SQL, use ``in``::

    >>> query = Post.where(Post.id._in(
    ...   Post.where(Post.id > 4).select(Fn.min(Post.id)),
    ...   Post.where(Post.id < 4).select(Fn.max(Post.id)),
    ... )).select(Post.id, Post.title)
    >>> [(post.id, post.title) for post in query]
    [(3L, u'Python GOOD'), (5L, u'Happy dog')]


Another way is using  ``limit``, get the next post::

    >>> query = Post.where(Post.id > 4).orderby(Post.id).limit(1).select(Post.title, Post.id)
    >>> query.sql
    "select post.title, post.id from post where post.id > '4' order by post.id limit 1 "

