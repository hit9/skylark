import sys

sys.path.insert(0, '..')

from CURD import Database, Model, Field, PrimaryKey, ForeignKey


class User(Model):
    name = Field()
    email = Field()


class Post(Model):
    post_id = PrimaryKey()
    name = Field()
    user_id = ForeignKey(point_to=User.id)
