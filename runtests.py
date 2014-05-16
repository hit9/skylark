#!/usr/bin/env python

import sys
from subprocess import call

if sys.hexversion < 0x03000000:
    PY_VERSION = 2
else:
    PY_VERSION = 3

base_cmd = ('DBAPI=%s NOSE_NOCAPTURE=1 '
            'nosetests -w tests -x -v --nologcapture --process-timeout=4;')

cmds = [base_cmd % 'pymysql', base_cmd % 'sqlite3']

if PY_VERSION == 2:
    cmds.insert(0, base_cmd % 'MySQLdb')

for cmd in cmds:
    exit_code = call(cmd, shell=True)

    if exit_code != 0:
        sys.exit(exit_code)
