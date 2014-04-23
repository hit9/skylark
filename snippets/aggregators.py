from models import User

count = User.count()
max_id = User.max(User.id)
min_id = User.min(User.id)
sum_of_ids = User.sum(User.id)
avg_of_ids = User.avg(User.id)
