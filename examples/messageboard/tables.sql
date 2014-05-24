create table if not exists message (
    id int primary key auto_increment,
    title varchar(100) default '',
    content text,
    create_at datetime
) engine=innodb default charset=utf8;
