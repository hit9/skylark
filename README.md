![](https://raw.githubusercontent.com/hit9/artworks/master/png/Skylark.png)
===========================================================================

A micro python orm for mysql and sqlite3. (Original named `CURD.py`).

Latest version: [v0.9.0](https://github.com/hit9/skylark/releases/tag/v0.9.0-LTS)

Development status: **4 - Beta**

Testing status: [![Build Status](https://travis-ci.org/hit9/skylark.png?branch=master)](https://travis-ci.org/hit9/skylark)

Sample Code
-----------

```python
>>> from models import User
>>> user = User(name='Tom', email='tom@gmail.com')
>>> user.save()  # insert
1
>>> user.email = 'tom@github.com'
>>> user.save()  # update
1
>>> [user.name for user in User.select()]  # select
[u'Tom']
>>> query = User.where(name='Tom').delete()
>>> query.execute()  # delete
1
>>> user = User.create(name='Kate', email='kate@gmail.com')  # another insert
>>> user.data
{'email': 'kate@gmail.com', 'name': 'Kate', 'id': 2}
>>> user.destroy()  # another delete
1
```

More examples: [sample/](sample/), [snippets](snippets/)

Requirements
------------

- Python >= 2.6 or >= 3.3

- For mysql users: [MySQLdb(MySQL-python)](https://pypi.python.org/pypi/MySQL-python) or [PyMySQL](https://github.com/PyMySQL/PyMySQL)

Install
-------

    $ pip install skylark

Documentation
-------------

Documentation: http://skylark.readthedocs.org/

Strongly recommend that you read [Quick Start](http://skylark.readthedocs.org/en/latest/quickstart.html) at first.

Sample App
----------

- A simple message board built with skylark and Flask: [examples/messageboard](examples/messageboard)

Tests
-----

- Status: [![Build Status](https://travis-ci.org/hit9/skylark.png?branch=master)](https://travis-ci.org/hit9/skylark)

- [How to Run Tests](tests/README.md)

License
-------

[LICENSE-BSD](LICENSE-BSD)

Changes
-------

[CHANGES](CHANGES)
