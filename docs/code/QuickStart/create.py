from models import User

User.create(name="Jack", email="Jack@github.com")  # the first way

user = User()  # use the instance of User
user.name = "Jack"
user.email = "Jack@github.com"
user.save()

# or this way

user = User(name="Jack", email="Jack@github.com")
user.save()
