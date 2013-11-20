CURD.py
=======

Tiny Python ORM for MySQL.
[![Build Status](https://travis-ci.org/hit9/CURD.py.png?branch=master)](https://travis-ci.org/hit9/CURD.py)

latest version: v0.3.1

Only support C, U, R, D, responsing to its name:

- Create

- Update

- Read

- Delete

- Multiple Tables

**NOTE**: CURD.py may not be stable before version v1.0

**NOTE**: CURD.py v0.3.0 has a lot of **Not-Backward-Compatible** changes.

Sample Code
-----------

```python
from CURD import Database, Model, Field

Database.config(user='root', passwd='', db='mytest')

class User(Model):
    name = Field()
    email = Field()

user = User(name='Join', email='Join@gmail.com')
user.save()
```

More examples are in [docs/sample/](http://github.com/hit9/CURD.py/tree/master/docs/sample).

Install
-------

    $ pip install CURD.py

Documents
---------

Documentaion is already on http://curdpy.readthedocs.org/

FAQ
---

1. I meet problem installing MySQL-python via pip.

  for ubuntu users:
  ```
  apt-get install libmysqlclient-dev
  ```

  for mac users:
  ```
  export PATH=$PATH:/usr/local/mysql/bin
  ```

2. Attention: CURD.py only works with tables which primarykey is generate by MySQL(Such as autoincement priamarykey integer).

License
-------

[LICENSE-BSD](https://github.com/hit9/CURD.py/blob/master/LICENSE-BSD)
