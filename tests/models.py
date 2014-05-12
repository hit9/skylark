# coding=utf8

import sys
sys.path.insert(0, '..')

from skylark import Model, PrimaryKey, Field, ForeignKey


class User(Model):
    name = Field()
    email = Field()


class Post(Model):
    post_id = PrimaryKey()
    name = Field()
    user_id = ForeignKey(User.id)
