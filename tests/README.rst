To run tests with nose::

    # create a database
    $ mysql -e 'create database curdtest;' -uroot -p 
    # add your mysql username and passwd
    $ vim mysql.conf
    # run this command in this directoryonf
    nosetests  -v
