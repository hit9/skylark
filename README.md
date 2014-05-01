![](http://i.imgur.com/fxvhCoN.png)
===================================

A nice micro orm for python, mysql only. (Original named `CURD.py`).

Latest version: [v0.7.0](https://github.com/hit9/skylark/releases/tag/v0.7.0)

Development status: **4 - Beta**

Testing status: [![Build Status](https://travis-ci.org/hit9/skylark.png?branch=master)](https://travis-ci.org/hit9/skylark)

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

Requirements
------------

- Python >= 2.6 or >= 3.3

- [MySQLdb(MySQL-python)](https://pypi.python.org/pypi/MySQL-python) or
[PyMySQL](https://github.com/PyMySQL/PyMySQL)

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

- A clean style blog system built with skylark and Flask: https://github.com/hit9/zhiz

FAQ
---

- [FAQ](http://skylark.readthedocs.org/en/latest/faq.html)

- [ISSUES TRACKER](https://github.com/hit9/skylark/issues)

Tests
-----

- Status: [![Build Status](https://travis-ci.org/hit9/skylark.png?branch=master)](https://travis-ci.org/hit9/skylark)

- [How to Run Tests](tests/README.rst)

License
-------

[LICENSE-BSD](LICENSE-BSD)

Changes
-------

[CHANGES](CHANGES)
