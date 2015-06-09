# coding=utf8

from skylark import Database, Model, Field


Database.config(user='root', passwd='', db='mydb')


class User(Model):
    name = Field()
    email = Field()


user = User(name='Join', email='Join@gmail.com')
user.save()
