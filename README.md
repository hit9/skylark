Note
----

virgo is undering dev now . Not stable

virgo
=====

Simple and easy to use ORM module for MySQL Database and Python 2

Yes,She is young ,so I call her 'virgo'.

Install
-------

virgo requires [MySQL-python](http://pypi.python.org/pypi/MySQL-python/) module.

```
pip install virgo
```

or 

```
git clone https://github.com/hit9/virgo
cd virgo
[sudo] python setup.py install
```

Sample Codes
------------

codes works with virgo looks like ..

```python
from virgo import *

Database.config(db = "mydb", user = "root", passwd = "123456")

class User(Model):
    name = Field()
    email = Field()

user = User(name = "Liming", email = "Liming@github.com")

user.save() # insert

user = User.where(name = "Liming").select().fetchone() # select,and fetch one result

print user.email
```

virgo only support CURD

Sample codes for multiple tables:

```python
class User(Model):
    name = Field()
    email = Field()

class Post(Model):
    post_id = PrimaryKey() # default primary key is id
    name = Field()
    user_id = ForeignKey(User.id)

for post,user in (Post & Post).select().fetchall():
    print "user:%s post's name:%s" %(user.name, post.name)
```

**Like virgo ? Star it On Github!**

Tests
-----

See [tests/](https://github.com/hit9/virgo/tree/master/tests)

Document
--------

See [doc/](https://github.com/hit9/virgo/tree/master/doc)

License:BSD
-----------

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
