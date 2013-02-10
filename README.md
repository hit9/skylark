CURD.py
=======

Tiny Python ORM for MySQL.

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
User.create(User.name == "Join", User.email == "Join@gmail.com")
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
    
See [sample/](sample/) for more.

License
-------

See [LICENSE](LICENSE)
