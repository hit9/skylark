from models import User, Post

User.create(name='Amy', email='Amy@gmail.com')  # return an instance of User

User.create(User.name == 'Join', User.email == 'Join@gmail.com')

user = User(name='Mark', email='Mark@github.com')
user.save()  # return 1 or 0 for success or failure

post = Post()
post.name = 'Hello World'
post.user_id = 1
post.save()
