from models import User, Post

# get the first user
first_user = User.at(1).getone()
print first_user.name

# get user who called 'Join'
jack = User.where(name='jack').getone()

# get all users
for user in User.select():
    print user.name

# have a look at who has written posts
for user, post in User.join(Post).select(User.name, Post.name):
    print 'Author: %s, PostName: %s' % (user.name, post.name)
