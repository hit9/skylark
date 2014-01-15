Message-Board
-------------

Sample app with CURD.py.

How to Run
----------

1. create table `message` in mysql:

   ```bash
   $ mysql -uusername -p
   ```

   create table in some database:

   ```sql
   mysql> source tables.sql
   ```

2. edit `config.py`.

3. install requirements.

   ```bash
   $ pip install -r requirements.txt
   $ python runserver.py
   ```

And then go to `http://localhost:5000` in browser.
