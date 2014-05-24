create table t_post (
    post_id integer primary key autoincrement,
    name varchar(100),
    user_id integer,
    foreign key(user_id) references t_user(id)
);
