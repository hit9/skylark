CURD.py
=======

Tiny Python ORM for MySQL. 
[![Build Status](https://travis-ci.org/hit9/CURD.py.png?branch=dev)](https://travis-ci.org/hit9/CURD.py)

Support:

- Create

- Update

- Read

- Delete

- Transaction

- Mult-Table

Sample Code
-----------

```python
# create
User.create(name="Join", email="Join@gmail.com")
# update
User.at(2).update(email="Join@github.com")
# read
join = User.where(name="Join").select().fetchone()
# have a look at who has written posts
for post, user in (Post & User).select().fetchall():
    print "Author: %s, PostName: %s" % (user.name, post.name)
# delete
User.at(3).delete()
# sytactic sugar
user = User[1]  # get the first user
users = User[:]  # select all users
users = User[3:7]  # primarykey between 3 and 7
# if some user in table named "Join"
user = User(name="Join")
print user in User
```

See [sample/](https://github.com/hit9/CURD.py/tree/master/sample) for more.

Install
-------

    pip install git+git://github.com/hit9/CURD.py.git@0.2.1

DOC
---

See [docs/](https://github.com/hit9/CURD.py/tree/master/docs).

License
-------

See [LICENSE](https://github.com/hit9/CURD.py/blob/master/LICENSE)
