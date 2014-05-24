from models import User, Post

# delete user from post, user where post.user_id = user.id
query = (Post & User).delete(User)  # mysql supports; sqlite3 dosenot support
