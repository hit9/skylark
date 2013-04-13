from CURD import Database, Model, Field, PrimaryKey, ForeignKey, Sugar


class User(Model):
    name = Field()
    email = Field()


class Post(Model):
    name = Field()
    post_id = PrimaryKey()
    user_id = ForeignKey(User.id)

Database.config(db="mydb", user="root", passwd="")

User.create(name="John", email="John@gmail.com")  # create

User.at(2).update(email="John@github.com")  # update

John = User.where(name="John").select().fetchone()  # read

# who wrote posts?
for post, user in (Post & User).select().fetchall():
    print "Author: %s, PostName: %s" % (user.name, post.name)

User.at(3).delete()  # delete

# sytactic sugar
user = User[1]  # 1st user
users = User[:]  # all users
users = User[3:7]  # users whose id between 3 and 7

user = User(name="John")
print user in User  # anyone in database named "John"?
