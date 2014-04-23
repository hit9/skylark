from models import User


query = User.at(2).update(email='Join@github.com')
query.execute()  # return rows updated

user = User.where(User.email == 'Join@github.com').getone()
user.email = 'Join123@github.com'
user.save()
