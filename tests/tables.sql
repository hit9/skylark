/*

desc user:
+-------+-------------+------+-----+---------+----------------+
| Field | Type        | Null | Key | Default | Extra          |
+-------+-------------+------+-----+---------+----------------+
| id    | int(11)     | NO   | PRI | NULL    | auto_increment |
| name  | varchar(33) | YES  |     | NULL    |                |
| email | varchar(33) | YES  |     | NULL    |                |
+-------+-------------+------+-----+---------+----------------+

desc post:
+---------+--------------+------+-----+---------+----------------+
| Field   | Type         | Null | Key | Default | Extra          |
+---------+--------------+------+-----+---------+----------------+
| post_id | int(11)      | NO   | PRI | NULL    | auto_increment |
| name    | varchar(100) | YES  |     | NULL    |                |
| user_id | int(11)      | YES  |     | NULL    |                |
+---------+--------------+------+-----+---------+----------------+

*/
create table user(
    id int primary key auto_increment, 
    name varchar(33), 
    email varchar(33)
) engine=InnoDB; 
create table post(
    post_id int primary key auto_increment,
    name varchar(100), 
    user_id int
) engine=InnoDB; 
