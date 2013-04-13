from models import User

User.at(3).delete()  # return rows deleted

user = User.at(2).select().fetchone()
user.destroy()  # return 0/1
