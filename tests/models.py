import sys

sys.path.append("..")

from CURD import Database, Model, Field, PrimaryKey, ForeignKey


class User(Model):
    name = Field()
    email = Field()


class Post(Model):
    post_id = PrimaryKey()
    name = Field()
    user_id = ForeignKey(point_to=User.id)
