from models import User


# return 0 or 1
User.at(2).update(email='Join@github.com')

user = User.where(User.email == 'Join@github.com').select().fetchone()

user.email = 'Join123@github.com'

user.save()
