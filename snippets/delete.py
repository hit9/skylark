from models import User

User.at(1).delete()  # 1L

user = User.at(2).getone()
user.destroy()  # 2L
