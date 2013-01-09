from virgo import *

Database.config(db="mydb", user="root", passwd="123456")


class User(Model):
    name = Field()
    email = Field()


class Post(Model):
    post_id = PrimaryKey()
    name = Field()
    user_id = ForeignKey(User.id)
