create table t_post(
    post_id serial primary key,
    name varchar(100),
    user_id int references t_user(id)
)
