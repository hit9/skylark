from skylark import fn, distinct
from models import User

# select count(distinct(user.name)) from user
query = User.select(fn.count(distinct(User.name)))
result = query.execute()
func = result.one()
return func.count
