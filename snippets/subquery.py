from models import User, Post

# select user.id, user.name, user.email from user where user.id in ((select post.user_id from post))
query = User.where(User.id._in(Post.select(Post.user_id))).select()
