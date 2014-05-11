How to run tests
-----------------

1. Install Requirements:

    pip install toml.py
    pip install nose
    pip install MySQLdb
    pip install pymysql
    pip install psycopg2

2. Create databases:

   for mysql(user: `root`, passwd: ``):
   ```
   mysql> create database skylarktests;
   ```

   for sqlite3: Nothing;

   for postgres(user: `postgres`, password: ``)
   ```
   =# create user postgres with password "";
   =# create database skylarktests with encoding "utf8";
   =# grant all privileges on database skylarktests to postgres;
   ```
