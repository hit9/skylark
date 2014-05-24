from models import User
from skylark import fn, sql

# create data..
User.create(name='jack')
User.create(name='jack')
User.create(name='foo')

# select count(user.id) as count_id, user.name from user group by user.name having count_id >= '2'
query = User.groupby(User.name).having(
    sql('count_id') >= 2
).select(fn.count(User.id).alias('count_id'), User.name)
result = query.execute()

for row in result.tuples():
    print row[0]  # count of id
    print row[1]  # user's name
