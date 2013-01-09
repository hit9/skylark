from models import User

user = User(name="Mark")

if user not in User:
    user.save()
else:
    exit("Already in database!")
