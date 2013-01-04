#
# models for virgo example
#

from virgo import *

Database.config(db="mydb", user="root", passwd="123456")


# define models:

class User(Model):
    name = Field()
    email = Field()


class Post(Model):
    post_id = PrimaryKey()
    name = Field()
    user_id = ForeignKey(User.id)


# user defined methods..

@classmethod
def Model_get(cls, key):
    return cls.at(key).select().fetchone()

Model.get = Model_get
