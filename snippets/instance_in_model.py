from models import User

user = User(name='jack')

if user in User:
    print 'Some one in table is named jack'
