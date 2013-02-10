To run tests with nose::

    mysql -e 'create database curdtest;'  # create a database
    vim mysql.conf  # add your mysql username and passwd
    nosetests  -v  # run this command in this directory
