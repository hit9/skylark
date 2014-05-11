create table t_post(
    post_id int primary key auto_increment,
    name varchar(100),
    user_id int,
    foreign key(user_id) references t_user(id)
) engine=innodb  default charset=utf8
