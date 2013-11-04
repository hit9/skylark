from models import User


User.at(2).update(email='Join@github.com')

user = User.where(User.email == 'Join@github.com').select().fetchone()

user.email = 'Join123@github.com'

user.save()
