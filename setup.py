# -*- coding: utf-8 -*-

"""
CURD.py
-------

Tiny Python ORM for MySQL.

Sample Usage
````````````

.. code:: python

    >>> from models import User
    >>> user = User(name='Tom', email='tom@gmail.com')
    >>> user.save()  # insert
    1L
    >>> user.email = 'tom@github.com'
    >>> user.save()  # update
    1L
    >>> [user.name for user in User.select()]  # select
    [u'Tom']
    >>> query = User.where(name='Tom').delete()
    >>> query.execute()  # delete
    1L
    >>> user = User.create(name='Kate', email='kate@gmail.com')  # another insert
    >>> user.data
    {'email': 'kate@gmail.com', 'name': 'Kate', 'id': 2L}
    >>> user.destroy()  # another delete
    1L

Installation
````````````

.. code:: bash

    $ pip install CURD.py

Links
`````

* `Documentation <http://curdpy.readthedocs.org/>`_
* `Code on Github <https://github.com/hit9/CURD.py>`_

**NOTICE**: CURD.py may not be stable before version 1.0

"""

from setuptools import setup


setup(
    name='CURD.py',
    version='0.4.1',
    author='hit9',
    author_email='nz2324@126.com',
    description=('Tiny Python ORM for MySQL'),
    license='BSD',
    keywords='CURD ORM MySQL Python tiny database',
    url='https://github.com/hit9/CURD.py',
    py_modules=['CURD'],
    install_requires = ['MySQL-python'],
    long_description=__doc__,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Database',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
