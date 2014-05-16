How to run tests
-----------------

1. Install Requirements:

   ```
   pip install toml.py nose MySQL-python pymysql
   ```

2. Create databases:

   for mysql(user: `root`, passwd: ``):
   ```sql
   mysql> create database skylarktests;
   ```

   for sqlite3: None.

3. Run tests:

   ```bash
   chmod u+x ./runtests.sh
   ./runtests.sh
   ```
