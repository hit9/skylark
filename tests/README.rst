To run tests with nose

1. create a database::

    $ mysql -e 'create database skylarktests;' -uroot -p 

2. add your mysql username and passwd::

    $ vim mysql.conf

3. run this command in this directoryonf::

    $ nosetests  -v
