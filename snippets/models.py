import MySQLdb
from skylark import Database, Model, Field, PrimaryKey, ForeignKey


class User(Model):
    name = Field()
    email = Field()


class Post(Model):
    name = Field()
    post_id = PrimaryKey()
    user_id = ForeignKey(User.id)

Database.set_dbapi(MySQLdb)
Database.config(db='mydb', user='root', passwd='')
