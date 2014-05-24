from models import User
from skylark import fn

query = User.at(1).select(User.name.alias('un'))
result = query.execute()
user = result.one()
user.un  # retrieve `name` by user.un

query = User.select(fn.count(User.name))
result = query.execute()
result.tuples()[0][0]  # retrieve count result by result.tuples()
