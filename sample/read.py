from models import User, Post

# get the first user
first_user = User.at(1).getone()
print first_user.name

# get user who called 'Join'
jack = User.where(name='jack').getone()

# get all users
for user in User.select():
    print user.name

# have a look at posts written by 'jack'

[post.name
 for post in Post.join(User).where(User.name == 'jack').select(Post.name)]
