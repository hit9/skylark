How to run tests
-----------------

1. Install Requirements:

   ```
   pip install toml.py nose MySQL-python pymysql psycopg2
   ```

2. Create databases:

   for mysql(user: `root`, passwd: ``):
   ```sql
   mysql> create database skylarktests;
   ```

   for sqlite3: None.

   for postgres(user: `postgres`, password: ``)
   ```sql
   =# create user postgres with password "";
   =# create database skylarktests with encoding "utf8";
   =# grant all privileges on database skylarktests to postgres;
   ```

3. Run tests:

   ```bash
   chmod u+x ./runtests.sh
   ./runtests.sh
   ```
