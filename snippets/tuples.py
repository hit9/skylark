from models import User

query = User.select()
results = query.execute()
return results.tuples()  # generator, each yield like: (1L, 'jack', 'jack@gmail.com')
