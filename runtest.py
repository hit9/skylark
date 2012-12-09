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
user.save()

#insert

another_user = User.create(username = "hi", email = "yes")

#select by primarykey

user3 = User.find(10)

if user3:
    print "found!"
    # update
    user3.username = "en"
    user3.save()
else:
    print "not found"

