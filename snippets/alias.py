from models import User
from skylark import fn

query = User.at(1).select(User.name.alias('un'))
result = query.execute()
user = result.one()
assert user.un  # retrieve `name` by user.un

query = User.select(fn.count(User.name).alias('count_name'))
result = query.execute()
func = result.one()
assert func.count_name  # retrieve count result by func.count_name
