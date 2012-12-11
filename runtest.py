#                   #####
##                   ####
### TEST CODE SO FAR  ###
####                   ##      
#####                   #

from virgo import *

Database.config(db = "mydb", user = 'root', passwd = "123456", charset = "utf8")

class User(Model):
    username = Field()
    email = Field()
    #set primarykey, default is id

user = User()

# insert 
user.username = "hello"
user.email = "email"
user.save() # return 0 for failure, else return id

# or like this:

user = User(username = "hello", email = "email")

user.save()

#insert

another_user = User.create(username = "hi", email = "yes")

#select 

for user in User.select(): # select all, return a generator object
    print user.id, user.email # etc

# to select a few fields, but not all:

User.select(User.username, User.id)

# where

for user in User.where((User.id >=  1)  & (User.email  ==  "hit9@hit9.org")).select():
    print user.username

# select a single record by primarykey

user = User.get(10) #if not found, return None

# delete

User.where(User.id == 13).delete() # return 0 for failure, else return rownumber deleted

#or like this:

user.destroy() #return 0 or 1

#update

user.username = "updatename"
user.save() #do a save on created object equal to update
