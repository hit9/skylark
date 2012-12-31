from models import *

# create one record

user = User.create(name="jack", email="jack@github.com")

print user._id  # get primary key's value

# create one record with method 'save'

user = User(name="myname")

user.save()  # return id

# update this user

user.email = "newemail"

user.save()

# if user in User table?

print user in User

# update, return updated rows number
print User.where(name="myname").update(name="newname")

# delete

user.destroy()

# or this way:
User.at(2).delete()

# join query

for user, post in (User & Post).where(
    User.id == Post.user_id
).select().fetchall():
    print user, post

# user defined method for Model

user = User.get(3)
