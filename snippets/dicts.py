from models import User

query = User.select()
results = query.execute()
return results.dicts()  # generator, each yield like: {'name': 'xxx', 'email': 'xxx'}
