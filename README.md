Simple ORM module for MySQL Database & Python

Under Dev now..


Sample Code:

```python

from virgo import *

Database.config(db = "mydb", user = 'root', passwd = "123456", charset = "utf8")

class User(Model):
    username = Field()
    email = Field()

for user in User.where((User.id >=  1)  & (User.email  ==  "hit9@hit9.org")).select():
    print user.username

```

For more sample codes, see `runtest.py`


Star virgo !
