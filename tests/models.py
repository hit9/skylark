# coding=utf8

import sys
sys.path.insert(0, '..')

from skylark import Model, PrimaryKey, Field, ForeignKey


class BaseModel(Model):
    table_prefix = 't_'


class User(BaseModel):
    name = Field()
    email = Field()


class Post(BaseModel):
    post_id = PrimaryKey()
    name = Field()
    user_id = ForeignKey(User.id)
