CURD.py
=======

Tiny Python ORM for MySQL.
[![Build Status](https://travis-ci.org/hit9/CURD.py.png?branch=master)](https://travis-ci.org/hit9/CURD.py)

latest version: v0.3.4

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
>>> from models import User
>>> user = User(name='Tom', email='tom@gmail.com')
>>> user.save()  # insert
1L
>>> user.email = 'tom@github.com'
>>> user.save()  # update
1L
>>> [user.name for user in User.select()]
[u'Tom']  # select
>>> query = User.where(name='Tom').delete()
>>> query.execute()  # delete
1L
>>> user = User.create(name='Kate', email='kate@gmail.com')  # anthor insert
>>> user.data
{'email': 'kate@gmail.com', 'name': 'Kate', 'id': 2L}
>>> user.destroy()  # anthor delete
1L
```

More examples are in [docs/sample/](http://github.com/hit9/CURD.py/tree/master/docs/sample).

Install
-------

    $ pip install CURD.py

Documentation
-------------

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

2. CURD.py only works with tables which has primarykey.

License
-------

[LICENSE-BSD](https://github.com/hit9/CURD.py/blob/master/LICENSE-BSD)

Changes
-------

See [CHANGES](CHANGES)
