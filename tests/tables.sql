/*
mysql> desc user;
+-------+-------------+------+-----+---------+----------------+
| Field | Type        | Null | Key | Default | Extra          |
+-------+-------------+------+-----+---------+----------------+
| id    | int(11)     | NO   | PRI | NULL    | auto_increment |
| name  | varchar(33) | YES  |     | NULL    |                |
| email | varchar(33) | YES  |     | NULL    |                |
+-------+-------------+------+-----+---------+----------------+
3 rows in set (0.04 sec)

mysql> desc post;                                                                                                                       
+---------+--------------+------+-----+---------+----------------+
| Field   | Type         | Null | Key | Default | Extra          |
+---------+--------------+------+-----+---------+----------------+
| post_id | int(11)      | NO   | PRI | NULL    | auto_increment |
| name    | varchar(100) | YES  |     | NULL    |                |
| user_id | int(11)      | YES  | MUL | NULL    |                |
+---------+--------------+------+-----+---------+----------------+
3 rows in set (0.00 sec)

 */
create table user(
    id int primary key auto_increment, 
    name varchar(33), 
    email varchar(33)
) engine=innodb; 
create table post(
    post_id int primary key auto_increment,
    name varchar(100),
    user_id int,
    foreign key(user_id) references user(id)
) engine=innodb; 
