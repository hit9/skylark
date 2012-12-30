How To run tests
------------

```
mysql>create database mydb;  # create a database in your mysql

vim mysql.conf # edit config file:user, passwd, db(your created last step)

nosetests runtests.py

mysql>drop database mydb; 
```
