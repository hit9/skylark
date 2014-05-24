from models import User

User.at(1).delete()  # rows affected

user = User.at(2).getone()
user.destroy()  # rows affected
