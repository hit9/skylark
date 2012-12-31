#
# models for virgo example
#

from virgo import *


# define models:

class User(Model):
    name = Field()
    email = Field()


class Post(Model):
    post_id = PrimaryKey()
    name = Field()
    user_id = Field()


# user defined methods..

@classmethod
def Model_get(cls, key):
    return cls.at(key).select().fetchone()

Model.get = Model_get
