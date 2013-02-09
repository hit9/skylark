from models import User

user = User[1]  # <=> User.at(1).select().fetchone()

users = User[:]  # select all users

users = User[3:7]  # select users whose primarykey between 3 and 7

user = User(name="Join")
print user in User  # if some user in table named "Join"
