from models import User

User.at(1).update(name='tom')  # 1L

user = User.at(1).getone()
user.save()  # 1L
