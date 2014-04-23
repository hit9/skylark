CURD.py (v0.5.0 - Beta)
=======================

Tiny Python ORM for MySQL.

Latest version: v0.5.0

Development status: 4 - Beta

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

More examples: [sample/](sample/), [snippets](snippets/)

Install
-------

    $ pip install CURD.py

Documentation
-------------

Documentation: http://curdpy.readthedocs.org/

Strongly recommend that you read [Quick Start](http://curdpy.readthedocs.org/en/latest/quickstart.html) at first.

Sample App
----------

A simple message board built with CURD.py and Flask: [examples/messageboard](examples/messageboard)

FAQ
---

- [FAQ](http://curdpy.readthedocs.org/en/latest/faq.html)

- [ISSUES TRACKER](https://github.com/hit9/CURD.py/issues)

Tests
-----

- Status: [![Build Status](https://travis-ci.org/hit9/CURD.py.png?branch=master)](https://travis-ci.org/hit9/CURD.py)

- [How to Run Tests](https://github.com/hit9/CURD.py/blob/dev/tests/README.rst)

License
-------

[LICENSE-BSD](https://github.com/hit9/CURD.py/blob/master/LICENSE-BSD)

Changes
-------

[CHANGES](CHANGES)

Feedback
--------

WE NEED YOU HELP!! CURD.py is young and may have a lot of bugs, don't be shy to
share your opinions or to report your issues, please open an issue on
https://github.com/hit9/CURD.py/issues.
