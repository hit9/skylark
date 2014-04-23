from models import User

# select user.id, user.name, user.email from user where user.id < '4'
query = User.where(User.id < 4).select()

# select user.id, user.name, user.email from user where user.id <= '4'
query = User.where(User.id <= 4).select()

# select user.id, user.name, user.email from user where user.id > '4'
query = User.where(User.id > 4).select()

# select user.id, user.name, user.email from user where user.id >= '4'
query = User.where(User.id >= 4).select()

# select user.id, user.name, user.email from user where user.id = '4'
query = User.where(User.id == 4).select()

# select user.id, user.name, user.email from user where user.id <> '4'
query = User.where(User.id != 4).select()

# select user.id, user.name, user.email from user where (user.id > '4'
# and user.id < '7')
User.where((User.id > 4) & (User.id < 7)).select()

# select user.id, user.name, user.email from user where (user.id = '4'
# or user.id = '7')
User.where((User.id == 4) | (User.id == 7)).select()

# select user.id, user.name, user.email from user where user.name like '%abc'
User.where(User.name.like('%abc')).select()

# select user.id, user.name, user.email from user where user.id
# between '4' and '7'
User.where(User.id.between(4, 7)).select()

# select user.id, user.name, user.email from user where user.id in ('5', '6')
User.where(User.id._in(5, 6)).select()

# select user.id, user.name, user.email from user where user.id
# not in ('5', '6')
User.where(User.id.not_in(5, 6)).select()
