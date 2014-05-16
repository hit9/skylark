#!/bin/bash
DBAPI=MySQLdb NOSE_NOCAPTURE=1 nosetests -w tests -x -v --nologcapture --process-timeout=4;
DBAPI=pymysql NOSE_NOCAPTURE=1 nosetests -w tests -x -v --nologcapture --process-timeout=4;
DBAPI=sqlite3 NOSE_NOCAPTURE=1 nosetests -w tests -x -v --nologcapture --process-timeout=4;
