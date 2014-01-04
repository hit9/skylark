CURD.py
=======

Tiny Python ORM for MySQL.
[![Build Status](https://travis-ci.org/hit9/CURD.py.png?branch=master)](https://travis-ci.org/hit9/CURD.py)

latest version: v0.4.0

Only support C, U, R, D, responsing to its name:

- Create

- Update

- Read

- Delete

**NOTE**: CURD.py may not be stable before version v1.0

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
>>> [user.name for user in User.select()]  # select
[u'Tom']
>>> query = User.where(name='Tom').delete()
>>> query.execute()  # delete
1L
>>> user = User.create(name='Kate', email='kate@gmail.com')  # another insert
>>> user.data
{'email': 'kate@gmail.com', 'name': 'Kate', 'id': 2L}
>>> user.destroy()  # another delete
1L
```

More examples: [docs/sample/](http://github.com/hit9/CURD.py/tree/master/docs/sample).

Install
-------

    $ pip install CURD.py

Documentation
-------------

http://curdpy.readthedocs.org/

Strongly recommend that you read [Quick Start](http://curdpy.readthedocs.org/en/latest/quickstart.html) at first.

FAQ
---

- [FAQ](http://curdpy.readthedocs.org/en/latest/faq.html)

- [ISSUES TRACKER](https://github.com/hit9/CURD.py/issues)

License
-------

[LICENSE-BSD](https://github.com/hit9/CURD.py/blob/master/LICENSE-BSD)

Changes
-------

[CHANGES](CHANGES)
