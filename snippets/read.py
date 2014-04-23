from models import User

# user at id=1
user = User.at(1).getone()
user = User.findone(id=1)

# all users
users = User.getall()

# user 2 < id < 5
users = User.findall(User.id > 2, User.id < 5)
