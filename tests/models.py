import sys

sys.path.insert(0, '..')

from CURD import Model, Field, PrimaryKey, ForeignKey


class User(Model):
    name = Field()
    email = Field()


class Post(Model):
    post_id = PrimaryKey()
    name = Field()
    user_id = ForeignKey(User.id)


class TestCustomTableName(Model):
    table_name = 'a_custom_table_name'


class TestTableName(Model):
    pass
