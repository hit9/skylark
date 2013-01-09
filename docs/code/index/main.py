from models import *

user = User(nam="Liming", email="Liming@github.com")
user.save()

user = User.where(name="Liming").select().fetchone()
print user.email

for post, user in (Post & User).select().fetchall():
    print "user %s post's name is %s" % (user.name, post.name)
