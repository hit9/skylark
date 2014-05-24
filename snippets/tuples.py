from models import User

query = User.select()
results = query.execute()
return results.tuples()  # tuple of rows, each row like: (1L, 'jack', 'jack@gmail.com')
