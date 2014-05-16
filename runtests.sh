#!/bin/bash
[ -z "$TRAVIS_PYTHON_VERSION" ] && TRAVIS_PYTHON_VERSION='2.7';

if [[ $TRAVIS_PYTHON_VERSION == '2.7' ]] || [[ $TRAVIS_PYTHON_VERSION == '2.6' ]]; then
  DBAPI=MySQLdb NOSE_NOCAPTURE=1 nosetests -w tests -x -v --nologcapture --process-timeout=4;
fi;
DBAPI=pymysql NOSE_NOCAPTURE=1 nosetests -w tests -x -v --nologcapture --process-timeout=4;
DBAPI=sqlite3 NOSE_NOCAPTURE=1 nosetests -w tests -x -v --nologcapture --process-timeout=4;
