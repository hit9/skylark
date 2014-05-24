from models import User

user = User.create(name='jack', email='jack@gmail.com')  # model instance

user = User(name='Kate', email='kate@gmail.com')
user.save()  # last insert id
