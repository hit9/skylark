from models import User

# select user.id from user where (user.id > '1' and (user.name = 'jack' or user.email = 'abc@abc.com'))
User.where(
    (User.id > 1) & ((User.name == 'jack') | (User.email == 'abc@abc.com'))
).select(User.id)
