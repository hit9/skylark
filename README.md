CURD.py
=======

Tiny Python ORM for MySQL. 
[![Build Status](https://travis-ci.org/hit9/CURD.py.png?branch=master)](https://travis-ci.org/hit9/CURD.py)

Support:

- Create

- Update

- Read

- Delete

- Transaction [In Plan]

- Mult-Table

Sample Code
-----------

```python
from CURD import Database, Model, Field, PrimaryKey, ForeignKey, Sugar


class User(Model):
    name = Field()
    email = Field()


class Post(Model):
    name = Field()
    post_id = PrimaryKey()
    user_id = ForeignKey(User.id)

Database.config(db="mydb", user="root", passwd="")

User.create(name="John", email="John@gmail.com")  # create

User.at(2).update(email="John@github.com")  # update

John = User.where(name="John").select().fetchone()  # read

# who wrote posts?
for post, user in (Post & User).select().fetchall():
    print "Author: %s, PostName: %s" % (user.name, post.name)

User.at(3).delete()  # delete

# sytactic sugar
user = User[1]  # 1st user
users = User[:]  # all users
users = User[3:7]  # users whose id between 3 and 7
```

See [docs/sample/](https://github.com/hit9/CURD.py/tree/master/docs/sample) for more.

Install
-------

    pip install git+git://github.com/hit9/CURD.py.git@v0.2.3

FAQ
---

1. I meet problem installing MySQL-python via pip.

  for ubuntu users:
  ```
  apt-get install libmysqlclient-dev
  ```

  for mac users,run this command in your terminal:
  ```
  export PATH=$PATH:/usr/local/mysql/bin
  ```

2. Attention: CURD.py only works with tables which primarykey is generate by MySQL(Such as autoincement priamarykey integer).

Documents
---------

Documentaion is already on https://curdpy.readthedocs.org/

License
-------

See [LICENSE](https://github.com/hit9/CURD.py/blob/master/LICENSE-BSD)
