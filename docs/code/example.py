from CURD import Database, Model, Field

Database.config(db="mydb", user="root", passwd="")


class User(Model):
    name = Field()
    email = Field()

user = User(name="Jack", email="Jack@github.com")
user.save()
