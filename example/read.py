from models import User, Post

# get the first user
first_user = User.at(1).select().fetchone()
print first_user.name

# get user who called "Join"
join = User.where(name="Join").select().fetchone()

# get all users

for user in User.select().fetchall():
    print user.name
