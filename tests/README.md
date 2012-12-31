How To run tests
------------

Test virgo with nose.

```
mysql>create database testvirgo;  # create a database in your mysql

vim mysql.conf # edit config file:user, passwd, db(your created last step)

nosetests

mysql>drop database testvirgo; 
```
