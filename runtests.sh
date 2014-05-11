#!/bin/bash
DBAPI=MySQLdb NOSE_NOCAPTURE=1 nosetests -w tests -x -v --nologcapture
DBAPI=pymysql NOSE_NOCAPTURE=1 nosetests -w tests -x -v --nologcapture
DBAPI=sqlite3 NOSE_NOCAPTURE=1 nosetests -w tests -x -v --nologcapture
DBAPI=psycopg2 NOSE_NOCAPTURE=1 nosetests -w tests -x -v --nologcapture
