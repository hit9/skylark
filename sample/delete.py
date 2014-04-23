from models import User

query = User.at(3).delete()
query.execute()  # return rows deleted

user = User.at(2).getone()
user.destroy()  # return rows deleted
