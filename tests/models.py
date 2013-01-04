#
# models for tests
# see tables.sql for table structure
#

from virgo import *


class User(Model):
    name = Field()
    email = Field()


class Post(Model):
    post_id = PrimaryKey()
    name = Field()
    user_id = ForeignKey(point_to=User.id)
