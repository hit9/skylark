from models import User

user = User.create(name='jack', email='jack@gmail.com')

user = User(name='Kate', email='kate@gmail.com')
user.save()
