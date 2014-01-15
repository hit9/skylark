/*
 * mysql> desc message;
 * +-----------+--------------+------+-----+---------+----------------+
 * | Field     | Type         | Null | Key | Default | Extra          |
 * +-----------+--------------+------+-----+---------+----------------+
 * | id        | int(11)      | NO   | PRI | NULL    | auto_increment |
 * | title     | varchar(100) | YES  |     |         |                |
 * | content   | text         | YES  |     | NULL    |                |
 * | create_at | datetime     | YES  |     | NULL    |                |
 * +-----------+--------------+------+-----+---------+----------------+
 * 4 rows in set (0.05 sec)
 */


create table if not exists message (
    id int primary key auto_increment,
    title varchar(100) default '',
    content text default '',
    create_at datetime
) engine=innodb default charset=utf8;
