from models import User

User.at(1).update(name='tom')  # rows affected

user = User.at(1).getone()
user.save()  # rows affected
