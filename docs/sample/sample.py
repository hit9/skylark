# coding=utf8

from CURD import Database, Model, Field


Database.config(user="root", passwd="", db="mytest")


class User(Model):
    name = Field()
    email = Field()


user = User(name="Join", email="Join@gmail.com")
user.save()
